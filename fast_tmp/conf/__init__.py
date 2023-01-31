import importlib
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, validator

from fast_tmp.utils.db import init_model

logger = logging.Logger(__file__)


class Settings(BaseSettings):
    SECRET_KEY: str = ""  # 用户加密用字符串
    ALGORITHM: str = "HS256"
    AUTH_USER_MODEL_NAME: str = "User"
    AUTH_APP_NAME: str = "fast_tmp"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # token过期时间
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    FASTAPI_SETTINGS_MODULE: str = ""
    DEBUG: bool = True
    LOGIN_URL: str = "/api-token-auth"
    STATIC_ROOT = "static"
    STATIC_PATH = "static"
    MEDIA_ROOT = "media"
    MEDIA_PATH = "media"
    LOCAL_FILE: bool = False  # 是否使用本地amis静态文件

    @validator("ACCESS_TOKEN_EXPIRE_MINUTES", pre=True, allow_reuse=True)
    def set_token_out(cls, v: Any) -> int:
        if isinstance(v, str):
            v = int(v)
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must bigger than 0")
        return v

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
        workdir = os.getcwd()  # 把工作路径加入到代码执行里面
        if not self.FASTAPI_SETTINGS_MODULE:
            import toml  # type:ignore

            pyproject_path = os.path.join(workdir, "pyproject.toml")
            if os.path.exists(pyproject_path):
                with open(pyproject_path, "r") as f:
                    doc = toml.load(f)
                    if doc.get("tool") and doc["tool"].get("aerich"):
                        self.FASTAPI_SETTINGS_MODULE = doc["tool"]["aerich"]["tortoise_orm"]
                    elif doc.get("tool") and doc["tool"].get("fast-tmp"):
                        self.FASTAPI_SETTINGS_MODULE = doc["tool"]["fast-tmp"]["tortoise_orm"]
                    else:
                        logger.warning("envirment FASTAPI_SETTINGS_MODULE is null")
                # 去除后缀 只导入模块
                if self.FASTAPI_SETTINGS_MODULE.endswith(".TORTOISE_ORM"):
                    self.FASTAPI_SETTINGS_MODULE = self.FASTAPI_SETTINGS_MODULE.replace(
                        ".TORTOISE_ORM", ""
                    )
            else:
                logger.warning("envirment FASTAPI_SETTINGS_MODULE is null")
        try:
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
                if hasattr(self, setting) and not os.getenv(setting):
                    setattr(self, setting, setting_value)
                else:
                    env_val = os.getenv(setting)
                    self.EXTRA_SETTINGS[setting] = (
                        type(setting_value)(env_val) if env_val else setting_value
                    )

    def _init_model(self):
        if not getattr(self, "TORTOISE_ORM"):
            import warnings

            warnings.warn("TORTOISE_ORM为空")
        else:
            init_model(self)  # fixme 如果提示 has no models,请检查是否在执行导入settings之前先导入了fast_tmp.model


settings = Settings()
settings._init_model()
