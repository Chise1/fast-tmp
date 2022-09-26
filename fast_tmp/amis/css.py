# -*- encoding: utf-8 -*-
"""
@File    : css.py
@Time    : 2021/1/1 14:08
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from pydantic import BaseModel


class Horizontal(BaseModel):
    left: int
    right: int
    offset: int
