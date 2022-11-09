# -*- encoding: utf-8 -*-
"""
@File    : style.py
@Time    : 2022/11/9 12:17
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from enum import Enum


class FormWidgetSize(
    str,
    Enum,
):
    full = "full"
    lg = "lg"  # 大
    md = "md"  # 中,默认值
    sm = "sm"  # 小
    xs = "xs"  # 极小


class Mode(str, Enum):
    horizontal = "horizontal"
    inline = "inline"
    normal = "normal"


class WidgetSize:
    lg = "lg"  # 大
    md = "md"  # 中,默认值
    sm = "sm"  # 小
    xs = "xs"  # 极小
