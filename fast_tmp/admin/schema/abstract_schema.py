from typing import Optional, TypeVar

from pydantic.main import BaseModel

from fast_tmp.admin.schema.enums import ActionTypeEnum, ButtonLevelEnum, ButtonSize, TypeEnum


class BaseAmisModel(BaseModel):
    type: TypeEnum


AmisModel = TypeVar("AmisModel", bound=BaseAmisModel)


class _Action(BaseAmisModel):
    type = TypeEnum.action
    label: str
    actionType: ActionTypeEnum
    icon: Optional[str]
    size: ButtonSize = ButtonSize.md
    level: ButtonLevelEnum = ButtonLevelEnum.primary
    tooltip: Optional[str]  # 鼠标挪上去的提示


class Message(BaseModel):
    fetchSucss: Optional[str]
    fetchFailed: Optional[str]
    saveSuccess: Optional[str]
    saveFailed: Optional[str]
