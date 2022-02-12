# ModelAdmin类说明

该类是整个项目的核心类，主要用于生成前端页面。 方法如下:

```python
from typing import Any, Tuple
from sqlalchemy import Column


class ModelAdmin:
    model: Any  # sqlalchemy的model，如果model存在多对多字段，则model暂时只支持单主键
    # list
    list_display: Tuple[Column, ...] = ()  # 在前端显示的内容，注意，如果要支持修改和删除功能，这里必须有类的主键
    list_per_page: int = 10  # 每页显示数量
    list_max_show_all: int = 200  # 最大每页数量
    # create
    create_fields: Tuple[Column, ...] = ()  # 创建页面需要的字段，如果有关系型字段（多对多，多对一，一对多，一对一等）则不要使用关系字段对应的外键字段，目前暂时只支持多对一和多对多
    update_fields: Tuple[Column, ...] = ()  # 同create_fields
    methods: Tuple[str, ...] = ("list", "create", "update", "delete",)  # 支持的方法 

    @classmethod
    def get_create_dialogation_button(cls):  # 新增按钮，如果要自定义按钮可重构这里
        ...

    @classmethod
    def get_list_page(cls):  # list页面展示的字段
        ...

    @classmethod
    def pks(cls):  # 获取主键
        ...

    @classmethod
    def get_del_one_button(cls):  # 删除按钮
        ...

    @classmethod
    def get_update_one_button(cls):  # 更新按钮和页面
        ...

    @classmethod
    def get_operation(cls):  # 生成每条数据后面的按钮面板,要增加自定义按钮可以在这里增加
        ...

    @classmethod
    def get_crud(cls):  # 获取整个页面的json模型
        ...

    @classmethod
    def get_app_page(cls):  # 获取页面
        ...

    @classmethod
    def create_model(cls, data: dict):
        """
        写入数据库之前调用
        """
        ...

    @classmethod
    def update_model(cls, instance: Any, data: dict) -> Any:
        """
        更新数据之前调用
        """
        ...

    @classmethod
    def get_list_sql(cls):  # 获取显示list的sql
        ...

    @classmethod
    def get_one_sql(cls, pks: list):  # 获取update使用的sql
        ...
```