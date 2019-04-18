from flask import Flask, url_for, render_template, redirect, request, jsonify, flash, abort, g, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, User
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
app = Flask(__name__)
engine = create_engine('sqlite:///cat-app.db')
Base.metadata.bind = engine
web_session = session


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')


@auth.verify_password
def verify_password(username, password):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/profile/<int:id>')
@auth.login_required
def get_login(id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=id).one()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('protected_resources.html', user=user, categories=categories)


@app.route('/login/', methods=['POST', 'GET'])
def login_page():
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
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('public_page.html', categories=categories, items=reversed(items))


@app.route('/<string:categoryName>/items')
def show_details(categoryName):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(Category).filter_by(title=categoryName).one()
    items = session.query(Item).filter_by(category=category.title).all()
    return render_template('items.html', items=items, category=category)


def create_user():
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
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    #catalog = []
    #for c in categories:
    #    catalog.append(c.serialize)
    #    items = session.query(Item).filter_by(category_id=c.id).all()
    #    catalog[-1]['Items'] = [i.serialize for i in items]
    #return jsonify(Categories=catalog)
    return jsonify(Item=[item.serialize for item in items])

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.secret_key = "Super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
