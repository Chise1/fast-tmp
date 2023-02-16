from typing import List, Optional, TypeVar

from pydantic.main import BaseModel

from fast_tmp.amis.enums import ActionTypeEnum, ButtonLevelEnum, ButtonSize


class SchemaNode(BaseModel):
    """
    所有amis类的父类
    """

    type: str


class Tpl(SchemaNode):
    type = "tpl"
    tpl: str


SchemaArray = TypeVar("SchemaArray", bound=List[SchemaNode])


class _Action(SchemaNode):
    """
    操作按钮
    """

    type = "button"
    label: str
    actionType: ActionTypeEnum
    icon: Optional[str]
    size: Optional[ButtonSize] = None
    level: ButtonLevelEnum = ButtonLevelEnum.primary
    tooltip: Optional[str]  # 鼠标挪上去的提示
    className: Optional[str]


class Message(BaseModel):
    """
    消息框
    """

    fetchSucss: Optional[str]
    fetchFailed: Optional[str]
    saveSuccess: Optional[str]
    saveFailed: Optional[str]
