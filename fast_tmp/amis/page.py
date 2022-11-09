from typing import List, Optional, Tuple, Union

from fast_tmp.amis.base import BaseAmisModel


class Page(BaseAmisModel):
    type = "page"
    title: Optional[str]
    subTitle: Optional[str]
    remark: Optional[str]
    aside: Optional[Union[BaseAmisModel, List[BaseAmisModel]]]  # 往页面的边栏区域加内容
    toolbar: Optional[
        Union[BaseAmisModel, List[BaseAmisModel]]
    ]  # 往页面的右上角加内容，需要注意的是，当有 title 时，该区域在右上角，没有时该区域在顶部
    body: List[BaseAmisModel] = []
    initApi: Optional[str]  # 获取初始数据
    initFetch: Optional[bool]  # 是否进行初始数据获取

    _list_fields: Tuple[str, ...] = ()
    _update_fields: Tuple[str, ...] = ()
    _create_fields: Tuple[str, ...] = ()


class HBox(BaseAmisModel):
    type = "hbox"
    className: Optional[str]
    columns: List[BaseAmisModel]


#
# class AppPage(BaseModel):
#     """
#     app的子页
#     """
#
#     label: str
#     icon: str
#     url: str
#     schema_: Page = Field(..., alias="schema")
#     # schemaApi: Optional[str] = None
#     link: Optional[str] = None
#     redirect: Optional[str] = None
#     rewrite: Optional[str] = None
#     isDefaultPage: Optional[str] = None
#
#     # visible:Optional[bool]=None
#     def dict(self, *args, **kwargs):
#         kwargs["exclude_none"] = True
#         res: dict = super().dict(*args, **kwargs)
#         return res


# class AppPageGroup(BaseModel):
#     label: str
#     children: List[AppPage]


# class App(BaseAmisModel):
#     type = TypeEnum.app
#     api: Optional[str]  # 页面配置接口，如果你想远程拉取页面配置请配置。返回配置路径 json>data>pages，具体格式请参考 pages 属性。
#     brandName: str  # 应用名称
#     logo: Optional[str]  # 图片地址或svg
#     header: Optional[BaseModel]  # 顶部区域
#     asideBefore: Optional[BaseModel]  # 页面菜单上前面区域
#     asideAfter: Optional[BaseModel]  # 页面菜单下前面区域
#     footer: Optional[BaseModel]  # 页面
#     pages: List[AppPageGroup]  # 具体页面数组，地一层为label集合，真正的页面在第二层开始
