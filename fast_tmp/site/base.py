import logging
from typing import Any, Coroutine, Dict, Optional

from starlette.requests import Request
from tortoise import fields
from tortoise.models import Model
from tortoise.queryset import QuerySet

from fast_tmp.amis.forms import Column, Control
from fast_tmp.amis.page import Page
from fast_tmp.amis.response import AmisStructError

logger = logging.getLogger(__file__)


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

    async def set_value(self, request: Request, obj: Model, value: Any) -> Optional[Coroutine]:
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


# 操作数据库的方法
class ModelSession:
    async def list(
        self,
        request: Request,
        perPage: int = 10,
        page: int = 1,
    ):
        """
        获取列表
        """
        pass

    async def get_instance(self, request: Request, pk: Any) -> Optional[Model]:
        """
        根据pk获取一个实例
        """
        pass

    async def patch(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        """
        对inline的数据进行更新
        """
        pass

    async def create(self, request: Request, data: Dict[str, Any]) -> Model:
        pass


class RegisterRouter:
    _name: str
    _prefix: str

    async def get_app_page(self, request: Request) -> Page:
        raise AttributeError("need write")

    def __init__(self, prefix: str, name: str):
        self._name = name
        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix

    @property
    def name(self) -> str:
        return self._name


# 操作数据库的方法
class DbSession:
    async def list(
        self,
        request: Request,
        perPage: int = 10,
        page: int = 1,
    ):
        """
        获取列表
        """
        pass

    async def get_instance(self, request: Request, pk: Any) -> Optional[Model]:
        """
        根据pk获取一个实例
        """
        pass

    async def patch(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        """
        对inline的数据进行更新
        """
        pass

    async def create(self, request: Request, data: Dict[str, Any]) -> Model:
        pass

    async def delete(self, request: Request, pk: str):
        pass

    async def put_get(self, request: Request, pk: str) -> dict:
        pass

    async def select_options(
        self,
        request: Request,
        name: str,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
    ):
        pass

    async def put(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        pass
