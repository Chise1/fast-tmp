from typing import List, Optional

from pydantic import BaseModel

from fast_tmp.amis.base import BaseAmisModel
from fast_tmp.amis.column import AbstractControl


class Form(BaseAmisModel):
    type = "form"
    name: Optional[str]
    title: Optional[str]
    submitText: Optional[str]
    wrapWithPanel: Optional[bool]
    api: Optional[str]
    initApi: Optional[str]
    # interval: int = 3000??
    primaryField: Optional[str]  # 设置主键"id"
    body: List[AbstractControl]


class FilterModel(BaseModel):
    title: str = "过滤"
    body: List[dict]
    actions: List[dict] = [
        {"type": "submit", "level": "primary", "label": "查询"}
    ]  # type submit label  https://aisuda.bce.baidu.com/amis/zh-CN/components/crud#%E6%95%B0%E6%8D%AE%E6%BA%90%E6%8E%A5%E5%8F%A3%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E8%A6%81%E6%B1%82
