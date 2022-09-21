from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel


class BaseRes(BaseModel):
    status: int = 0
    msg: str = ""
    data: Any = {}


key_error = BaseRes(status=400, msg="主键错误")
not_found_instance = BaseRes(status=404, msg="找不到对象")
not_found_model = HTTPException(status_code=200, detail=BaseRes(msg="找不到对象").dict())
single_pk = HTTPException(status_code=200, detail=BaseRes(msg="暂时只支持单主键").dict())


class FastTmpError(HTTPException):
    pass


class NoAuthError(FastTmpError):
    def __init__(self):
        self.status_code = 401
        self.detail = BaseRes(msg="未登录").dict()


class TmpValueError(FastTmpError):
    def __init__(self):
        self.status_code = 401
        self.detail = BaseRes(msg="值错误").dict()
