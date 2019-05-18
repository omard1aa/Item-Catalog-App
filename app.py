from flask import Flask, url_for, render_template, redirect, request, jsonify,\
    flash, abort, g, session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, User
import random, string
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

auth = HTTPBasicAuth()
app = Flask(__name__)
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine
web_session = login_session

CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')


def login_required(f):
    @wraps(f)
    def x(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return x


@auth.verify_password
def verify_password(username, password):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:' \
              ' 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/profile/<int:id>')
@auth.login_required
def get_login(id):
    # This function is responsible for retrieving private page for authenticated user
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=id).one()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    if 'username' not in login_session:
        return redirect(url_for('login_page'))
    return render_template('protected_resources.html', user=user, categories=categories)


@app.route('/login/', methods=['POST', 'GET'])
def login_page():
    # This function is responsible for authenticating user and give permissions to be logged in
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        web_session['username'] = request.form['username']
        user = session.query(User).filter_by(username=username).first()
        if not user:
            flash('user not found')
            return render_template('login_page.html')
        if not user.verify_password(password):
            flash('Incorrect password!')
            return render_template('login_page.html')
        if user:
            return redirect(url_for('get_login', id=user.id))

    return render_template('login_page.html')


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    # This function is responsible for creating new account for new users.
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        if username == '' or password == '':
            flash('Sorry, invalid inputs!')
            return render_template('register_page.html')
        elif session.query(User).filter_by(username=username).first():
            flash('Sorry, existing user!')
            return render_template('register_page.html')
        elif password != password_confirm:
            flash('Passwords do not match')
            return render_template('register_page.html')
        else:
            newUser = User(username=username)
            newUser.hash_password(password)
            session.add(newUser)
            session.commit()
            flash('Congratulations! you have created your new account!\nLogin now to have more privileges')
            return redirect(url_for('login_page'))
    else:
        return render_template('register_page.html')


@app.route('/main', methods=['GET'])
def show_for_public():
    # This function is responsible for show the public page for the public
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('public_page.html', categories=categories, items=reversed(items))


@app.route('/<string:categoryName>/items')
def show_details(categoryName):
    # This function is responsible for showing category items in each category
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(Category).filter_by(title=categoryName).one()
    items = session.query(Item).filter_by(category=category.title).all()
    return render_template('items.html', items=items, category=category)


def create_user():
    # This function is responsible for adding new user to database
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    form_username = request.form['username']
    form_password = request.form['password']
    form_passwordConfirm = request.form['password_confirm']
    if form_username is not None and form_password is not None and form_passwordConfirm is not None:
        if form_password == form_passwordConfirm:
            form_username = request.form['username']
            form_password = request.form['password']
            newUser = User(username=form_username, password=form_password)
            session.add(newUser)
            session.commit()
            return newUser.username
            flash("Welcome, %s " %newUser.username)
        else:
            print('no matched passwords')
            flash("Passwords do not match!")
    else:
        flash("Sorry, Invalid info")


@app.route('/<string:categoryName>/new-item', methods=['GET', 'POST'])
@auth.login_required
def add_item(categoryName):
    # This function is responsible for allowing authenticating users to add new items to a category.
    if request.method == 'POST':
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        name = request.form['name']
        description = request.form['description']
        if session.query(Item).filter_by(name=name, category=categoryName).first():
            flash('Sorry, %s already exists in %s' %(name, categoryName))
            return render_template('new_item.htm', categoryname=categoryName)
        else:
            item = Item(name=name, category=categoryName, description=description)
            session.add(item)
            session.commit()
            flash('%s added to %s' %(name,categoryName))
    return render_template('new_item.htm', categoryname=categoryName)


@app.route('/delete/<int:itemid>/<string:itemname>', methods=['GET', 'POST'])
@auth.login_required
def delete_item(itemid, itemname):
    # This function is responsible for allowing authenticating users to delete items from a category.
    if request.method == 'POST':
        print('item id ', itemid)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        item = session.query(Item).filter_by(id=itemid).first()
        session.delete(item)
        session.commit()
        return redirect(url_for('show_details', categoryName=item.category))
    else:
        return render_template('delete_item.htm', itemid=itemid, itemname=itemname)


@app.route('/edit/<string:itemname>', methods=['GET', 'POST'])
@auth.login_required
def edit_item(itemname):
    # This function is responsible for allowing authenticating users to update items in categories.
    if request.method == 'POST':
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        new_name = request.form['name']
        new_desc = request.form['description']
        item = session.query(Item).filter_by(name=itemname).first()
        item.name = new_name
        if new_desc != '':
            item.description = new_desc
        session.commit()
        flash('%s has been updated to %s!' %(itemname, new_name))
        return redirect(url_for('show_details', categoryName=item.category))
    else:
        return render_template('edit_item.htm', itemname=itemname)


@app.route('/catalog.json')
def json():
    # This page is made to retrieve all items and category JSON data
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    # catalog = []
    # for c in categories:
    #    catalog.append(c.serialize)
    #    items = session.query(Item).filter_by(category_id=c.id).all()
    #    catalog[-1]['Items'] = [i.serialize for i in items]
    # return jsonify(Categories=catalog)
    return jsonify(Item=[item.serialize for item in items])

@app.route('/category/<int:category_id>/items/json')
def show_category_JSON(category_id):
    # This page is made to retrieve items of specific category JSON data
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category=category.title).all()
    return jsonify(Item=[item.serialize for item in items])


@app.route('/category/<int:category_id>/item/<int:item_id>/json')
def menuItemJSON(category_id, item_id):
    # This page is made to retrieve a specific item of specific category JSON data
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id, category=category.title).one()
    return jsonify(Item=item.serialize)

@app.route('/logout')
def logout():
    login_session.pop('username')
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.secret_key = "Super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
