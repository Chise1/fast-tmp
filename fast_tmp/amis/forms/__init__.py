from typing import List, Optional

from fast_tmp.amis.base import BaseAmisModel
from fast_tmp.amis.control import AbstractControl


class Form(BaseAmisModel):
    type = "form"
    name: str
    title: Optional[str]
    submitText: Optional[str]
    wrapWithPanel: Optional[bool]
    api: str
    initApi: Optional[str]
    # interval: int = 3000??
    primaryField: Optional[str]  # 设置主键"id"
    body: List[AbstractControl]
