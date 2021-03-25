# -*- encoding: utf-8 -*-
"""
@File    : db.py
@Time    : 2021/3/25 9:09
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from typing import Dict
from tortoise import Tortoise


def init_model(settings):
    tortoise_setting = settings.TORTOISE_ORM
    apps: Dict[str, dict] = tortoise_setting['apps']
    for app_name, value in apps.items():
        Tortoise.init_models(value['models'], app_name)
