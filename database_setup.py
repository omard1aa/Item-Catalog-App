from __builtin__ import property

from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy import create_engine
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker, relationship
from passlib.apps import custom_app_context as pwd_context
Base = declarative.declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(64))

    def hash_password(self, password_to_be_hashed):
        self.password = pwd_context.encrypt(password_to_be_hashed)

    def verify_password(self, password_to_be_verified):
        return pwd_context.verify(password_to_be_verified, self.password)

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    title = Column(String(64), primary_key=True)
    
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
    category = Column(String(64), ForeignKey('category.title'))
    category_rel = relationship(Category)
#    category_id = Column(Integer, ForeignKey('category.id'))
 #   categoryid_rel = relationship(Category, foreign_keys=[category_id])

    description = Column(String(64))

    @property
    def serialize(self):
        return {
            'ID': self.id,
            'Name': self.name,
            'Category': self.category,
            'Description': self.description
        }


engine = create_engine('sqlite:///cat-app.db')
Base.metadata.create_all(engine)
