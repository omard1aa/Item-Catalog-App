from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext import declarative
from database_setup import Category, Base, Item, User


# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base = declarative.declarative_base()
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()


latest_items = []
# Categories
category1 = Category(title="Soccer", id=10)

session.add(category1)

category = Category(title="Basketball", id=2)

session.add(category)

category = Category(title="Baseball", id=3)

session.add(category)

category = Category(title="Frisbee", id=4)

session.add(category)

category = Category(title="Snowboarding", id=5)

session.add(category)

category = Category(title="Rock Climbing", id=6)

session.add(category)

category = Category(title="Foosball", id=7)

session.add(category)

category = Category(title="Skating", id=8)

session.add(category)

category = Category(title="Hockey", id=9)

session.add(category)

session.commit()
print "Categories added!"

# # # Category items
item = Item(name='Soccer Cleats', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Soccer')
session.add(item)

item = Item(name='Two Shinguars', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Soccer')
session.add(item)

item = Item(name='Shinguards', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Soccer')
session.add(item)

item = Item(name='Tshirt', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Basketball')
session.add(item)

item = Item(name='Basket', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Basketball')
session.add(item)

item = Item(name='Ball', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Basketball')
session.add(item)

item = Item(name='Goggles', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Snowboarding')
session.add(item)

item = Item(name='Snowboard', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Snowboarding')
session.add(item)

item = Item(name='Frisbee', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Frisbee')
session.add(item)

item = Item(name='Bat', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Baseball')
session.add(item)

item = Item(name='Jersey', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Soccer')
session.add(item)

item = Item(name='Stick', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Hockey')
session.add(item)

item = Item(name='Gloves', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Rock Climbing')
session.add(item)

item = Item(name='Helmet', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Rock Climbing')
session.add(item)

item = Item(name='Ball', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Foosball')
session.add(item)

item = Item(name='Short', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Foosball')
session.add(item)

item = Item(name='T-Shirt', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Foosball')
session.add(item)

item = Item(name='Cap', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Baseball')
session.add(item)

item = Item(name='Jacket', description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit.', category='Baseball')
session.add(item)

session.commit()
print "Category Items added!"
