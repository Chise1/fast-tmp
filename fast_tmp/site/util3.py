from typing import Optional, Any, Type, Tuple, List

from starlette.requests import Request
from tortoise import Model, fields
from tortoise.queryset import QuerySet

from fast_tmp.amis.forms import Column, Control, ColumnInline, QuickEdit, ControlEnum, SaveImmediately
from fast_tmp.amis.response import AmisStructError


class AbstractControl(object):
    """
    用户自定义的column组件
    """
    _prefix: Optional[str]  # 网段
    _field_name: Optional[str]
    control: Control

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

    def prefetch(self, request: Request, queryset: QuerySet, ) -> QuerySet:  # 列表
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

    async def get_column(self, request: Request) -> Column:
        """
        获取column模型
        """

    async def get_column_inline(self, request: Request) -> Column:
        """
        获取内联修改的column
        """

    async def get_control(self, request: Request) -> Control:
        """
        获取内联修改的column
        """

    def __init__(self, _field_name: str, _prefix: str, **kwargs):
        name = kwargs.get("name") or _field_name
        label = kwargs.get("label") or name
        self._prefix = _prefix
        if not _field_name:
            raise AmisStructError("field_name can not be none")
        self._field_name = _field_name
        kwargs["name"] = name
        kwargs["label"] = label
        self.control = Control(**kwargs)


class StrControl(AbstractControl):

    async def get_column(self, request: Request) -> Column:
        print(self.control.json())
        return Column.from_orm(self.control)

    async def get_control(self, request: Request) -> Control:
        return Control.from_orm(self.control)

    async def get_column_inline(self, request: Request) -> Column:
        if not self._prefix:
            raise AmisStructError("prefix can not be none")
        column = ColumnInline.from_orm(self.control)
        column.quickEdit = QuickEdit(
            type=ControlEnum.text,
            saveImmediately=SaveImmediately(api=self._prefix + "/patch/$pk")
        )
        return column

    async def set_value(self, request: Request, obj: Model, value: Any):
        setattr(obj, self._field_name, value)

    async def get_value(self, request: Request, obj: Model) -> Any:
        return getattr(obj, self._field_name)

    def filter_queryset(self, queryset: QuerySet, request: Request, filter: str) -> QuerySet:  # 列表
        return queryset.filter(**{self._field_name: filter})

    def search_queryset(self, queryset: QuerySet, request: Request, search: Any) -> QuerySet:  # 搜索
        """
        是否需要增加额外的查询条件
        值可以近似
        """
        return queryset.filter(**{self._field_name + "__contains": filter})


class IntControl(StrControl):
    async def get_column_inline(self, request: Request) -> Column:
        if not self._prefix:
            raise AmisStructError("prefix can not be none")
        column = ColumnInline.from_orm(self)
        column.quickEdit = QuickEdit(
            type=ControlEnum.number,
            saveImmediately=SaveImmediately(api=self._prefix + "/patch/$pk")
        )
        return column


def get_list_columns(
        model: Type[Model],
        prefix: str,
        include: Tuple[str, ...] = (),
        inline: Tuple[str, ...] = (),
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    todo：增加多对多字段显示
    """
    field_types = model._meta.fields_map

    res = []
    for field, field_type in field_types.items():
        if include and field not in include:
            continue
        if isinstance(field_type, fields.IntField):
            res.append(IntControl(_field_name=field, _prefix=prefix, ))

    return res


def create_column(
        field_name: str,
        field_type: fields.Field,
        prefix: str,
):
    if isinstance(field_type, fields.IntField):
        return IntControl(_field_name=field_name, _prefix=prefix, )
    elif isinstance(field_type, fields.CharField):
        return StrControl(_field_name=field_name, _prefix=prefix, )
    else:
        raise AmisStructError("create_column error:", type(field_type))
