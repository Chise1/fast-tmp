from typing import Any, List, Optional

from pydantic.main import BaseModel

from fast_tmp.admin.schema.abstract_schema import BaseAmisModel
from fast_tmp.admin.schema.enums import TypeEnum


class AmisPage(BaseModel):
    label: str
    icon: str
    url: str
    schemaApi: str  # 动态拉取页面
    link: Optional[str]  # 远程链接
    redirect: Optional[str]  # 跳转，当命中当前页面时，跳转到目标页面。
    rewrite: bool = False  # 改成渲染其他路径的页面，这个方式页面地址不会发生修改。
    isDefaultPage: Optional[str]  # 当你需要自定义 404 页面的时候有用，不要出现多个这样的页面，因为只有第一个才会有用。
    visible: bool = True
    className: Optional[str]  # 菜单类名


class AppSchema(BaseAmisModel):
    type = TypeEnum.app
    api: Optional[str]  # 动态拉取
    brandName: str  # 应用名称
    logo: Optional[str]
    className: Optional[str]
    header: Optional[BaseAmisModel]
    asideBefore: Optional[BaseAmisModel]
    asideAfter: Optional[BaseAmisModel]
    footer: Optional[BaseAmisModel]
    pages: List[Any] = []
    data: Any = None
