from typing import Any, Dict, List

from pydantic import BaseModel


class ListDataWithPage(BaseModel):  # 带分页的数据
    items: List[dict]
    total: int = 0


class BaseRes(BaseModel):
    status: int = 0
    msg: str = ""
    data: Any = {}


class FieldErrorRes(BaseRes):
    status: int = 422
    msg: str = ""
    data: Any = None
    errors: Dict[str, str]
