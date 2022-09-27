from typing import Any, Optional

from starlette.requests import Request
from tortoise import Model, fields
from tortoise.queryset import QuerySet

from fast_tmp.amis.forms import Column, Control
from fast_tmp.amis.response import AmisStructError


class AbstractAmisAdminDB:
    """
    admin访问model的数据库指令
    """

    _prefix: str  # 网段
    name: str

    def list_queryset(self, queryset: QuerySet) -> QuerySet:  # 列表
        """
        主要考虑是否需要预加载
        """
        return queryset

    def prefetch(self) -> Optional[str]:  # 列表
        """
        过滤规则，用于页面查询和过滤用
        要求值必须相等
        """
        return None

    async def get_value(self, request: Request, obj: Model) -> Any:
        """
        获取值
        """
        return getattr(obj, self.name)

    async def set_value(self, request: Request, obj: Model, value: Any):
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
        self.name = _field_name


class AmisOrm:
    def orm_2_amis(self, value: Any) -> Any:
        """
        orm的值转成amis需要的值
        """
        if callable(value):
            return value()
        return value

    def amis_2_orm(self, value: Any) -> Any:
        return value


class AbstractControl:
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


class ModelFilter:
    name = ""
    type: Optional[str] = None
    label: Optional[str]
    clearable: Optional[bool]
    placeholder: Optional[str]
    _field: Optional[fields.Field] = None

    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        return queryset

    def __init__(
        self,
        name: str,
        type: str = "input-text",
        label: str = None,
        clearable=None,
        placeholder=None,
        field: fields.Field = None,
    ):
        self.name = name
        self._field = field
        self.type = type
        self.label = label or self.name
        self.clearable = clearable
        self.placeholder = placeholder
