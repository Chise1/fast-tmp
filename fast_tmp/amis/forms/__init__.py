from typing import List, Optional

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

