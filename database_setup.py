from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy import create_engine
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker, relationship
from passlib.apps import custom_app_context as pwd_context
Base = declarative.declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    title = Column(String(64))

    @property
    def serialize(self):
        return {
            'ID': self.id,
            'Name': self.title,           
        }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    description = Column(String(64))
    category = Column(String(64))

    @property
    def serialize(self):
        return {
            'ID': self.id,
            'Name': self.name,
            'Category': self.category,
            'Description': self.description
        }


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(64))

    def hash_password(self, password_to_be_hashed):
        self.password = pwd_context.encrypt(password_to_be_hashed)

    def verify_password(self, password_to_be_verified):
        return pwd_context.verify(password_to_be_verified, self.password)
# engine = create_engine('sqlite:///catalog-app.db')

engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine
Base.metadata.create_all(engine)
