from typing import List, Optional

from pydantic import BaseModel


class Filter(BaseModel):
    type: str
    name: str
    label: str
    clearable: Optional[bool]
    placeholder: Optional[str]


class FilterModel(BaseModel):
    title: str = "条件搜索"
    body: List[Filter]
    actions: List[dict] = [
        {"type": "submit", "level": "primary", "label": "查询"}
    ]  # type submit label  https://aisuda.bce.baidu.com/amis/zh-CN/components/crud#%E6%95%B0%E6%8D%AE%E6%BA%90%E6%8E%A5%E5%8F%A3%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E8%A6%81%E6%B1%82
