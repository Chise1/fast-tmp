from typing import Any

from pydantic.main import BaseModel


class AmisRes(BaseModel):
    status: int = 0
    msg: str = ""
    data: Any = {}
