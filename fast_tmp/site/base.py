import datetime
import json
from typing import Any, Optional

from starlette.requests import Request
from tortoise import Model
from tortoise.queryset import QuerySet

from fast_tmp.amis.forms import Column, Control
from fast_tmp.amis.response import AmisStructError


class AbstractAmisAdminDB:
    """
    admin访问model的数据库指令
    """

    _prefix: Optional[str]  # 网段
    _field_name: Optional[str]

    def list_queryset(self, queryset: QuerySet) -> QuerySet:  # 列表
        """
        主要考虑是否需要预加载
        """
        return queryset

    def search_queryset(self, queryset: QuerySet, request: Request, search: Any) -> QuerySet:  # 搜索
        """
        是否需要增加额外的查询条件
        值可以近似
        """
        raise AmisStructError("未构建")

    def filter_queryset(self, queryset: QuerySet, request: Request, filter: Any) -> QuerySet:  # 列表
        """
        过滤规则，用于页面查询和过滤用
        要求值必须相等
        """
        raise AmisStructError("未构建")

    def prefetch(self, request: Request, queryset: QuerySet) -> QuerySet:  # 列表
        """
        过滤规则，用于页面查询和过滤用
        要求值必须相等
        """
        return queryset

    async def get_value(self, request: Request, obj: Model) -> Any:
        """
        获取值
        """
        return getattr(obj, self._field_name)

    async def set_value(self, request: Request, obj: Model, Any):
        """
        设置值
        """
        pass

    def validate(self, value: Any) -> Any:
        """
        对数据进行校验
        """
        return value

    def __init__(self, _field_name: str, _prefix: str, **kwargs):
        self._prefix = _prefix
        if not _field_name:
            raise AmisStructError("field_name can not be none")
        self._field_name = _field_name


class AmisOrm:
    def orm_2_amis(self, value: Any) -> Any:
        """
        orm的值转成amis需要的值
        """
        return value

    def amis_2_orm(self, value: Any) -> Any:
        return value


class AbstractControl(object):
    """
    用户自定义的column组件
    """

    def get_column(self, request: Request) -> Column:
        """
        获取column模型
        """

    def get_column_inline(self, request: Request) -> Column:
        """
        获取内联修改的column
        """

    def get_control(self, request: Request) -> Control:
        """
        获取内联修改的column
        """
