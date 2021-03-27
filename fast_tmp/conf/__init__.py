import importlib
import os

from ..utils.db import init_model
from . import global_settings

FASTAPI_VARIABLE = "FASTAPI_SETTINGS_MODULE"


class Settings:
    def __init__(self):
        settings_module = os.environ.get(FASTAPI_VARIABLE)
        if not settings_module:
            project_slug = os.path.split(os.getcwd())[1]
            os.environ.setdefault('FASTAPI_SETTINGS_MODULE', project_slug + ".settings")
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))
        self.SETTINGS_MODULE = settings_module
        try:
            mod = importlib.import_module(self.SETTINGS_MODULE)
        except Exception as e:
            raise ImportError(f"导入settings报错:{e}")

        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)
        if not getattr(self, "SECRET_KEY"):
            raise AttributeError("SECRET_KEY不能为空")
        if not getattr(self, "TORTOISE_ORM"):
            raise AttributeError("TORTOISE_ORM不能为空")
        else:
            init_model(self)


settings = Settings()
