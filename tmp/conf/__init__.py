import importlib
import os
from . import global_settings
from ..utils.db import init_model

FASTAPI_VARIABLE = "FASTAPI_SETTINGS_MODULE"


class Settings:
    def __init__(self):
        settings_module = os.environ.get(FASTAPI_VARIABLE)
        if not settings_module:
            raise ImportError("未找到settings.py" f"你必须设置环境变量{FASTAPI_VARIABLE}=你的settings.py的位置")
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))
        self.SETTINGS_MODULE = settings_module
        mod = importlib.import_module(self.SETTINGS_MODULE)
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
