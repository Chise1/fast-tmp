from typing import Optional, Union

from pydantic import HttpUrl
from pydantic.main import BaseModel

from .base import _Action
from .enums import ActionTypeEnum, ButtonLevelEnum, TypeEnum
from .frame import Dialog, Drawer


class FeedBack(BaseModel):  # 和弹窗一致
    title: str
    body: Union[str, BaseModel]


class ActionMessage(BaseModel):
    success: str = "操作成功"
    failed: str = "操作失败"


# 参考：https://baidu.gitee.io/amis/docs/components/action?page=1
class AjaxAction(_Action):
    """
    ajax请求
    """

    actionType = ActionTypeEnum.ajax
    confirmText: Optional[str] = None  # 如果配置了这个字段则会有弹出框提示
    api: str
    redirect: Optional[str] = None  # 如果配置路径，可以实现跳转
    feedback: Optional[FeedBack] = None
    # 如果重载需要携带参数，则可以输入：{"reload": "xxx?a=${a}&b=${b}"}
    reload: Optional[str] = None  # 可以把name传递过来，则请求成功自动刷新,页面刷新则为window，多个用逗号分开
    message: Optional[ActionMessage] = None  # 修改默认toast信息


# class LinkAction(_Action):
#     """
#     单页跳转(暂不支持)
#     """
#     actionType = ActionTypeEnum.link
#     level = ButtonLevelEnum.info
class UrlAction(_Action):
    """
    单页跳转(暂不支持)
    """

    actionType = ActionTypeEnum.url
    level = ButtonLevelEnum.success
    url: HttpUrl
    blank: bool = False


class CopyAction(_Action):
    """
    复制文本
    """

    actionType = ActionTypeEnum.copy
    content: str  # 制定要复制的内容


# class ReloadAction(_Action):
#     type = ActionTypeEnum.reload
#     target: str  # 需要刷新的目标组件名字（组件的name值，自己配置的），多个请用 , 号隔开。


class DialogAction(_Action):
    type = TypeEnum.button
    actionType = ActionTypeEnum.dialog
    dialog: Dialog


class DrawerAction(_Action):
    actionType = ActionTypeEnum.drawer
    drawer: Drawer
    # type = TypeEnum.button
