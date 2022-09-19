"""
展示页面需要的model
"""
from typing import List

from pydantic import BaseModel

from .forms import Column


class ZSTable(BaseModel):
    type: str = "table"
    title: str
    name: str
    source: str
    columns: List[Column]


class ZS(BaseModel):
    type: str = "service"
    api: str
    body: BaseModel
