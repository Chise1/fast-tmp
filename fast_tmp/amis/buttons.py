# -*- encoding: utf-8 -*-
"""
@File    : buttons.py
@Time    : 2021/1/2 17:13
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import List

from fast_tmp.amis.base import _Action
from fast_tmp.amis.enums import TypeEnum
from fast_tmp.amis.forms import Column


class Operation(Column):
    type = TypeEnum.operation
    label = "操作"
    buttons: List[_Action] = []
    name: str = ""
