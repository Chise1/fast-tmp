from typing import Tuple, Dict, Callable, Type, Union

from pydantic import BaseModel


class ModelAdmin(BaseModel):
    list_display: Tuple[str, ...] = ()
    list_display_links: Tuple[str, ...] = ()
    list_per_page: int = 10
    list_max_show_all: int = 200
    offset: int = 0
    search_fields = ()
    fields: Tuple[Union[str,BaseModel], ...] = ()
    exclude: Tuple[Union[str,BaseModel], ...] = ()
    actions: Tuple[str, ...] = ("list", "retrieve", "create", "put", "delete", "deleteMany")
    actions_func: Dict[
        str, Callable] = {}  # 请求对应的调用函数，"list","retrieve","create","put","delete","deleteMany"有默认自定义方法，这里如果填了就是覆盖默认方法
    # 页面相关的东西
    page_model: Type[BaseModel]
