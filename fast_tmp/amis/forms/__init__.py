from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from fast_tmp.amis.abstract_schema import BaseAmisModel
from fast_tmp.amis.enums import TypeEnum
from fast_tmp.amis.forms.enums import ControlEnum, FormWidgetSize, ItemModel


class SelectOption(BaseModel):
    label: str
    value: Union[int, str]


# fixme:未来考虑更多的fields类型字段支持
class Column(BaseModel):
    """
    用于列表等的显示
    """

    type: Optional[ControlEnum]  # 把这个和schema获取的参数进行融合，保证schema获取的值可以使用
    name: str  # type: ignore
    label: str


class QuickEdit(BaseModel):
    model: str = "inline"
    type: ControlEnum
    saveImmediately: Optional[bool]
    options: Optional[List[Union[SelectOption, str, int]]]
    clearable: Optional[bool]
    format: Optional[str]
    validations: Optional[Dict[str, Union[int, str]]]  # 注意，键值对请参考ValidateEnum


class ColumnInline(Column):
    """带内联的功能"""

    quickEdit: Optional[QuickEdit]  # can not be none

    class Config:
        orm_mode = True


class Mapping(Column):
    """
    专门用来作为枚举显示用的
    """

    type = ControlEnum.mapping
    map: Dict[Union[int, str], str]  # map的值可以是html片段


class AbstractControl(Column):
    pass


class Form(BaseAmisModel):
    type = TypeEnum.form
    name: str
    title: Optional[str]
    submitText: Optional[str]
    wrapWithPanel: Optional[bool]
    api: str
    initApi: Optional[str]
    # interval: int = 3000??
    primaryField: Optional[str]  # 设置主键"id"
    body: List[AbstractControl]


class Control(AbstractControl):
    """
    用户form表单等写入
    """

    value: Optional[Any]  # 默认值
    labelRemark: Optional[str]  # 表单项标签描述
    description: Optional[str]  # 描述
    placeholder: Optional[str]  # 描述
    inline: Optional[bool]  # 内联样式
    submitOnChange: Optional[bool]  # 是否该表单项值发生变化时就提交当前表单。
    disabled: Optional[bool]
    disableOn: Optional[str]  # 配置规则查看https://baidu.gitee.io/amis/docs/components/form/formitem
    visible: Optional[bool]
    visibleOn: Optional[str]  # 配置规则查看https://baidu.gitee.io/amis/docs/components/form/formitem
    required: Optional[bool]
    requiredOn: Optional[str]
    hidden: Optional[bool]  # 可使用条件配置如 this.number>1
    hiddenOn: Optional[str]  # 配置判定逻辑
    validations: Optional[Dict[str, Union[int, str]]]  # 注意，键值对请参考ValidateEnum
    validationErrors: Optional[
        Dict[str, str]  # todo tortoise-orm的校验转这里
    ]  # 注意，键值对请参考ValidateEnum，举例："minimum": "同学，最少输入$1以上的数字哈",其中$1为该错误的数据
    className: Optional[str]  # 表单最外层类名
    inputClassName: Optional[str]  # 表单控制器类名
    labelClassName: Optional[str]  # label 的类名
    mode: Optional[ItemModel]
    size: Optional[FormWidgetSize]

    class Config:
        orm_mode = True
