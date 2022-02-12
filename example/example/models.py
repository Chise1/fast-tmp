import time
from typing import List

from sqlalchemy import String, Boolean, Integer, DateTime, DECIMAL, Float, JSON, Text, Time, Column, ForeignKey
# todo Image,File
from sqlalchemy.orm import relationship

from fast_tmp.models import Base


class UserInfo(Base):
    __tablename__ = "userinfo"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    age = Column(Integer, default=10, )
    birthday = Column(DateTime)
    money = Column(DECIMAL(scale=3))
    height = Column(Float)
    info = Column(JSON)
    tag = Column(Text)
    # create_time=Column(Time,default=time.time)
    is_superuser = Column(Boolean(), default=True)


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True)
    name = Column(String(32),nullable=False)
    books: List['Book'] = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'), info={"admin_name": "name"},nullable=False)  # todo 增加提示
    author: Author = relationship("Author", back_populates="books")
