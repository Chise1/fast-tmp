from typing import List, Optional, TypeVar, Union

from pydantic.main import BaseModel

from fast_tmp.amis.enums import ActionTypeEnum, ButtonLevelEnum, ButtonSize


class SchemaNode(BaseModel):
    """
    所有amis类的父类
    """

    type: str
    # grid布局
    columnClassName: Optional[str]
    xs: Optional[int]
    sm: Optional[int]
    md: Optional[int]
    lg: Optional[int]
    valign: Optional[str]  # 'top' | 'middle' | 'bottom' | 'between'


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
    actionType: Union[ActionTypeEnum, str]
    icon: Optional[str]
    size: Optional[Union[ButtonSize, str]] = None
    level: ButtonLevelEnum = ButtonLevelEnum.primary
    className: Optional[str]
    iconClassName: Optional[str]
    rightIcon: Optional[str]
    rightIconClassName: Optional[str]
    active: Optional[str]
    activeLevel: Optional[str]  # str 	- 	按钮高亮时的样式，配置支持同level。
    activeClassName: Optional[str]  # str 	is-active 	给按钮高亮添加类名。
    block: Optional[bool]  # boolean 	- 	用display:"block"来显示按钮。
    confirmText: Optional[str]  # 模板 	- 	当设置后，操作在开始前会询问用户。可用 ${xxx} 取值。
    reload: Optional[str]  # str 	- 	指定此次操作完后，需要刷新的目标组件名字（组件的name值，自己配置的），多个请用 , 号隔开。
    tooltip: Optional[str]  # str 	- 	鼠标停留时弹出该段文字，也可以配置对象类型：字段为title和content。可用 ${xxx} 取值。
    disabledTip: Optional[
        str
    ]  # 'str' | 'TooltipObject' -被禁用后鼠标停留时弹出该段文字，也可以配置对象类型：字段为title和content。可用 ${xxx} 取值。
    tooltipPlacement: Optional[
        str
    ]  # str 	top	如果配置了tooltip或者disabledTip，指定提示信息位置，可配置top、bottom、left、right。
    close: Optional[
        Union[bool, str]
    ]  # boolean or str 	- 	当action配置在dialog或drawer的actions中时，配置为true指定此次操作完后关闭当前dialog或drawer。当值为字符串，并且是祖先层弹框的名字的时候，会把祖先弹框关闭掉。
    required: Optional[List[str]]  # Array<str> 	- 	配置字符串数组，指定在form中进行操作之前，需要指定的字段名的表单项通过验证
    disabled: Optional[bool]
    disabledOn: Optional[str]


class Message(BaseModel):
    """
    消息框
    """

    fetchSucss: Optional[str]
    fetchFailed: Optional[str]
    saveSuccess: Optional[str]
    saveFailed: Optional[str]
