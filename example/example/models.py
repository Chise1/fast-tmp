import time

from sqlalchemy import String, Boolean, Integer, DateTime, DECIMAL, Float, JSON, Text, Time, Column
# todo Image,File
from fast_tmp.models import Base


class UserInfo(Base):
    __tablename__ = "userinfo"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    age = Column(Integer,default=10,)
    birthday=Column(DateTime)
    money=Column(DECIMAL(scale=3))
    height=Column(Float)
    info=Column(JSON)
    tag=Column(Text)
    # create_time=Column(Time,default=time.time)
    is_superuser = Column(Boolean(), default=True)
