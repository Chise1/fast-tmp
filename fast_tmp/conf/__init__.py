import importlib
import os
from typing import Any, Dict, List, Optional, Union

from fast_tmp.utils.db import init_model

FASTAPI_VARIABLE = "FASTAPI_SETTINGS_MODULE"

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    AUTH_USER_MODEL_NAME: str = "User"
    AUTH_APP_NAME: str = "fast_tmp"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_ENVIROMENT: str = "development"

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_TYPE: str = "mysql"
    TORTOISE_ORM: Optional[Dict[str, Any]] = None

    class Config:
        case_sensitive = True

    def __init__(self):
        super(Settings, self).__init__()
        settings_module = os.environ.get(FASTAPI_VARIABLE)
        if not settings_module:
            project_slug = os.path.split(os.getcwd())[1]
            settings_module = project_slug + ".settings"
        self.SETTINGS_MODULE = settings_module
        try:
            mod = importlib.import_module(self.SETTINGS_MODULE)
        except Exception as e:
            raise ImportError(f"导入settings报错:{e}")

        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)
        if not getattr(self, "TORTOISE_ORM"):
            import warnings

            warnings.warn("TORTOISE_ORM为空")
        else:
            init_model(self)


settings = Settings()
