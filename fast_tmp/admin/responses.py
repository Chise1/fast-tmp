from typing import Any

from pydantic import BaseModel


class BaseRes(BaseModel):
    status: int = 0
    msg: str = ""
    data: Any = {}


key_error = BaseRes(status=400, msg="主键错误")
not_found_instance = BaseRes(status=404, msg="找不到对象")
