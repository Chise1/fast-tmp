from typing import Any, List, Optional, Tuple, Type

from starlette.requests import Request
from tortoise import Model, fields
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance
from tortoise.queryset import QuerySet

from fast_tmp.amis.forms import (
    Column,
    ColumnInline,
    Control,
    ControlEnum,
    QuickEdit,
    QuickEditSelect,
)
from fast_tmp.amis.forms.widgets import SelectItem, SelectOption
from fast_tmp.amis.response import AmisStructError
from fast_tmp.responses import TmpValueError


class AbstractControl(object):
    """
    用户自定义的column组件
    """

    _prefix: Optional[str]  # 网段
    _field_name: Optional[str]
    _default: Any = None
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

    def prefetch(
        self,
        request: Request,
        queryset: QuerySet,
    ) -> QuerySet:  # 列表
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

    def __init__(self, _field_name: str, _prefix: str, _default: Any = None, **kwargs):
        name = kwargs.get("name") or _field_name
        label = kwargs.get("label") or name
        self._prefix = _prefix
        self._default = _default
        if not _field_name:
            raise AmisStructError("field_name can not be none")
        self._field_name = _field_name
        kwargs["name"] = name
        kwargs["label"] = label
        self.control = Control(**kwargs)


class BaseAdminControl(AbstractControl):
    """
    默认的将model字段转control的类
    """

    _field: fields.Field
    _control_type = ControlEnum.input_text

    async def get_column(self, request: Request) -> Column:
        ret = Column.from_orm(self.control)
        ret.type = ControlEnum.text
        return ret

    async def get_control(self, request: Request) -> Control:
        control = Control.from_orm(self.control)
        control.type = self._control_type
        control.value = self._default
        return control

    async def get_column_inline(self, request: Request) -> Column:
        if not self._prefix:
            raise AmisStructError("prefix can not be none")
        column = ColumnInline.from_orm(self.control)
        column.quickEdit = QuickEdit(type=ControlEnum.text, saveImmediately=True)
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

    def __init__(self, _field_name: str, _field: fields.Field, _prefix: str, **kwargs):
        super().__init__(_field_name, _prefix, _default=_field.default, **kwargs)
        self._field = _field
        if not self._field.null:
            self.control.required = True

    def validate(self, value: Any):
        self._field.validate(value)


class StrControl(BaseAdminControl):
    """
    基础的字符串control
    """


class TextControl(StrControl):
    _control_type = ControlEnum.textarea


class IntControl(BaseAdminControl):
    _control_type = ControlEnum.number

    async def get_column_inline(self, request: Request) -> Column:
        if not self._prefix:
            raise AmisStructError("prefix can not be none")
        column = ColumnInline.from_orm(self.control)
        column.quickEdit = QuickEdit(type=ControlEnum.number, saveImmediately=True)
        return column


class IntEnumControl(BaseAdminControl):
    def __init__(self, _field_name: str, _field: fields.Field, _prefix: str, **kwargs):
        super(IntEnumControl, self).__init__(_field_name, _field, _prefix, **kwargs)
        self.control.type = ControlEnum.select
        control = SelectItem.from_orm(self.control)
        if self._default is not None:
            control.value = self._default.name
        control.options = self.options()
        self.control = control

    async def get_value(self, request: Request, obj: Model) -> Any:
        ret = getattr(obj, self._field_name)
        if not ret:
            return "None"
        return ret.name

    async def set_value(self, request: Request, obj: Model, value: Any):
        if value == "None":
            setattr(obj, self._field_name, None)
            return
        for i in self._field.enum_type:
            if i.name == value:
                setattr(obj, self._field_name, i)
                return
        raise TmpValueError()

    def options(self) -> List[str]:
        res = []
        for i in self._field.enum_type:
            res.append(i.name)
        if self._field.null:
            res.insert(0, "None")
        return res

    async def get_column_inline(self, request: Request) -> Column:
        if not self._prefix:
            raise AmisStructError("prefix can not be none")
        column = ColumnInline.from_orm(self.control)
        column.type = None
        column.quickEdit = QuickEditSelect(
            type=ControlEnum.select, saveImmediately=True, options=self.options()
        )
        return column

    async def get_control(self, request: Request) -> Control:
        return self.control


class BooleanControl(IntEnumControl):
    def options(self) -> List[str]:
        if self._field.null:
            return ["None", "True", "False"]
        return ["True", "False"]

    def __init__(self, _field_name: str, _field: fields.Field, _prefix: str, **kwargs):
        super(IntEnumControl, self).__init__(_field_name, _field, _prefix, **kwargs)
        self.control.type = ControlEnum.select
        control = SelectItem.from_orm(self.control)
        if self._default is not None:
            control.value = "True" if self._default else "False"
        control.options = self.options()
        self.control = control

    async def get_value(self, request: Request, obj: Model) -> Any:
        val = getattr(obj, self._field_name)
        if val is None:
            return "None"
        elif val:
            return "True"
        else:
            return "False"

    async def set_value(self, request: Request, obj: Model, value: Any):
        if value == "None" or value is None:
            setattr(obj, self._field_name, None)
        elif value == "True" or value is True:
            setattr(obj, self._field_name, True)
        else:
            setattr(obj, self._field_name, False)

    async def get_control(self, request: Request) -> Control:
        return self.control


class StrEnumControl(IntEnumControl):
    pass


def create_column(
    field_name: str,
    field_type: fields.Field,
    prefix: str,
):
    if isinstance(field_type, IntEnumFieldInstance):
        return IntEnumControl(field_name, field_type, prefix)
    elif isinstance(field_type, CharEnumFieldInstance):
        return StrEnumControl(field_name, field_type, prefix)
    elif isinstance(field_type, (fields.IntField, fields.SmallIntField, fields.BigIntField)):
        return IntControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.TextField):
        return TextControl(field_name, field_type, prefix)

    elif isinstance(field_type, fields.CharField):
        return StrControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.BooleanField):
        return BooleanControl(field_name, field_type, prefix)

    else:
        raise AmisStructError("create_column error:", type(field_type))
