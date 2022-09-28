import importlib
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, validator

from fast_tmp.utils.db import init_model

FASTAPI_VARIABLE = "FASTAPI_SETTINGS_MODULE"
logger = logging.Logger(__file__)


class Settings(BaseSettings):
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    AUTH_USER_MODEL_NAME: str = "User"
    AUTH_APP_NAME: str = "fast_tmp"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    FASTAPI_SETTINGS_MODULE: str
    DEBUG: bool = True
    LOGIN_URL: str = "/api-token-auth"
    STATIC_ROOT = "static"
    STATIC_PATH = "static"
    LOCAL_FILE: bool = False  # 是否使用本地amis静态文件

    @validator("DEBUG", pre=True, allow_reuse=True)
    def get_debug(cls, v: str) -> bool:
        if isinstance(v, str):
            if v != "True":
                return False
        return True

    @validator("BACKEND_CORS_ORIGINS", pre=True, allow_reuse=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    TORTOISE_ORM: Optional[Dict[str, Any]] = None
    # 额外的配置信息
    EXTRA_SETTINGS: Dict[str, Any] = {}

    def __init__(self):
        super(Settings, self).__init__()
        if not self.FASTAPI_SETTINGS_MODULE:
            logger.warning("envirment FASTAPI_SETTINGS_MODULE is null")
        try:
            workdir = os.getcwd()  # 把工作路径加入到代码执行里面
            for path in sys.path:
                if path == workdir:
                    break
            else:
                sys.path.append(workdir)
            mod = importlib.import_module(self.FASTAPI_SETTINGS_MODULE)
        except Exception as e:
            raise ImportError(f"导入settings报错:{e}")

        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                if hasattr(self, setting):
                    setattr(self, setting, setting_value)
                else:
                    self.EXTRA_SETTINGS[setting] = setting_value

    def _init_model(self):
        if not getattr(self, "TORTOISE_ORM"):
            import warnings

            warnings.warn("TORTOISE_ORM为空")
        else:
            init_model(self)  # fixme 如果提示 has no models,请检查是否在执行导入settings之前先导入了fast_tmp.model


settings = Settings()
settings._init_model()
