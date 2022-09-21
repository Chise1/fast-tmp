import datetime
from typing import Any, List, Optional

from starlette.requests import Request
from tortoise import Model, fields
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance
from tortoise.queryset import QuerySet

from fast_tmp.amis.forms import Column, ColumnInline, Control, ControlEnum, QuickEdit
from fast_tmp.amis.forms.widgets import DateItem, DatetimeItem, SelectItem, TimeItem
from fast_tmp.amis.response import AmisStructError
from fast_tmp.responses import TmpValueError


class AbstractControl(object):
    """
    用户自定义的column组件
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

    def __init__(self, _field_name: str, _prefix: str, **kwargs):
        self._prefix = _prefix
        if not _field_name:
            raise AmisStructError("field_name can not be none")
        self._field_name = _field_name


class BaseAdminControl(AbstractControl):
    """
    默认的将model字段转control的类
    """

    name: str
    label: str
    _field: fields.Field
    _control: Control = None
    _column: Column = None
    _column_inline: ColumnInline = None
    _control_type: ControlEnum = ControlEnum.input_text

    async def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Column(type=ControlEnum.text, name=self.name, label=self.label)
        return self._column

    async def get_control(self, request: Request) -> Control:
        if not self._control:
            self._control = Control(type=self._control_type, name=self.name, label=self.label)
            if not self._field.null:
                self._control.required = True
            if self._field.default is not None:
                self._control.value = self.orm_2_amis(self._field.default)
        return self._control

    def options(self):
        return None

    async def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            column = await self.get_column(request)
            self._column_inline = ColumnInline(
                type=column.type,
                name=self.name,
                label=self.label,
                quickEdit=QuickEdit(type=self._control_type, saveImmediately=True),
            )
            options = self.options()
            if options:
                self._column_inline.quickEdit.options = options
                if self._field.null:
                    self._column_inline.quickEdit.clearable=True
        return self._column_inline

    async def set_value(self, request: Request, obj: Model, value: Any):
        setattr(obj, self._field_name, self.amis_2_orm(value))

    async def get_value(self, request: Request, obj: Model) -> Any:
        return self.orm_2_amis(getattr(obj, self._field_name))

    def filter_queryset(self, queryset: QuerySet, request: Request, filter: str) -> QuerySet:  # 列表
        return queryset.filter(**{self._field_name: filter})

    def search_queryset(self, queryset: QuerySet, request: Request, search: Any) -> QuerySet:  # 搜索
        """
        是否需要增加额外的查询条件
        值可以近似
        """
        return queryset.filter(**{self._field_name + "__contains": filter})

    def __init__(self, _field_name: str, _field: fields.Field, _prefix: str, **kwargs):
        super().__init__(_field_name, _prefix, **kwargs)
        self._field = _field
        self.name = kwargs.get("name") or _field_name
        self.label = kwargs.get("label") or self.name

    def validate(self, value: Any):
        self._field.validate(value)

    def orm_2_amis(self, value: Any) -> Any:
        """
        orm的值转成amis需要的值
        """
        return value

    def amis_2_orm(self, value: Any) -> Any:
        return value


class StrControl(BaseAdminControl):
    """
    基础的字符串control
    """


class TextControl(StrControl):
    _control_type = ControlEnum.textarea


class IntControl(BaseAdminControl):
    _control_type = ControlEnum.number


class IntEnumControl(BaseAdminControl):
    _control_type = ControlEnum.select

    async def get_control(self, request: Request) -> Control:
        if not self._control:
            await super().get_control(request)
            d = self._control.dict(exclude_none=True)
            d.pop("type")
            if self._field.null:
                d["clearable"] = True
            self._control = SelectItem(**d)
            self._control.options = self.options()
        return self._control

    def orm_2_amis(self, value: Any) -> Any:
        if value is not None:
            return value.name

    def amis_2_orm(self, value: Any) -> Any:
        if value is None and self._field.null:
            return None
        for i in self._field.enum_type:
            if i.name == value:
                return i.value
        raise TmpValueError(f"{self.label} 不能为 {value}")

    def options(self) -> List[str]:
        res = []
        for i in self._field.enum_type:
            res.append(i.name)
        return res


class BooleanControl(BaseAdminControl):
    _control_type = ControlEnum.select

    async def get_control(self, request: Request) -> Control:
        if not self._control:
            await super().get_control(request)
            d = self._control.dict(exclude_none=True)
            d.pop("type")
            if self._field.null:
                d["clearable"] = True
            self._control = SelectItem(**d)
            self._control.options = self.options()
        return self._control

    def options(self) -> List[str]:
        return ["True", "False"]

    def amis_2_orm(self, value: Any) -> Any:
        if (value == "None" or not value) and self._field.null:
            return None
        if value == "True":
            return True
        elif value == "False":
            return False
        raise TmpValueError()

    def orm_2_amis(self, value: Any) -> Any:
        if value is None:
            return "None"
        elif value:
            return "True"
        return "False"


class StrEnumControl(IntEnumControl):
    pass


class DateTimeControl(BaseAdminControl):
    _control_type = ControlEnum.datetime

    def amis_2_orm(self, value: Any) -> Any:
        if (value == "None" or not value) and self._field.null:
            return None
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    def orm_2_amis(self, value: datetime.datetime) -> Any:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


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
    elif isinstance(field_type, fields.DatetimeField):
        return DateTimeControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.CharField):
        return StrControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.BooleanField):
        return BooleanControl(field_name, field_type, prefix)

    else:
        raise AmisStructError("create_column error:", type(field_type))
