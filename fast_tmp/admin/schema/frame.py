# 弹框
from typing import List, Optional, Union

from pydantic.main import BaseModel

from .abstract_schema import _Action
from .enums import DialogSize


class Dialog(BaseModel):
    title: str
    nextCondition: bool = True
    size: DialogSize = DialogSize.md
    actions: Optional[List[_Action]]
    body: Union[str, BaseModel, dict]


# todo:尚未完成：https://baidu.gitee.io/amis/docs/components/dialog?page=1

# 抽屉
class Drawer(BaseModel):
    title: str
    body: Union[str, BaseModel]
    actions: Optional[Union[_Action, List[_Action]]] = None
