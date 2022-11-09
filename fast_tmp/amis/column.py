from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from fast_tmp.amis.base import _Action


class ColumnEnum(str, Enum):
    text = "text"
    mapping = "mapping"


class SelectOption(BaseModel):
    label: str
    value: Union[int, str]


class Column(BaseModel):
    """
    用于列表等的显示
    """

    type: Optional[str]  # 把这个和schema获取的参数进行融合，保证schema获取的值可以使用
    name: str  # type: ignore
    label: str


class QuickEdit(BaseModel):
    model: str = "inline"
    type: str
    saveImmediately: Optional[bool]
    options: Optional[List[Union[SelectOption, str, int]]]
    clearable: Optional[bool]
    format: Optional[str]
    validations: Optional[Any]  # 注意，键值对请参考ValidateEnum
    timeFormat: Optional[str]  # = "HH:mm:ss"  # 时间选择器值格式，更多格式类型请参考 moment
    inputFormat: Optional[str]  # "HH:mm:ss"  # 时间选择器显示格式，即时间戳格式，更多格式类型请参考 moment


class ColumnInline(Column):
    """带内联的功能"""

    quickEdit: QuickEdit  # can not be none

    class Config:
        orm_mode = True


class Mapping(Column):
    """
    专门用来作为枚举显示用的
    """

    type = "mapping"
    map: Dict[Union[int, str], str]  # map的值可以是html片段


class Operation(Column):
    type = "operation"
    label = "操作"
    buttons: List[_Action] = []
    name: str = ""
