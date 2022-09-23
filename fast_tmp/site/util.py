import datetime
import json
from typing import Any, List, Optional

from starlette.requests import Request
from tortoise import ForeignKeyFieldInstance, Model, fields
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance
from tortoise.queryset import QuerySet

from fast_tmp.amis.custom import Custom
from fast_tmp.amis.forms import Column, ColumnInline, Control, ControlEnum, QuickEdit
from fast_tmp.amis.forms.widgets import (
    DateItem,
    DatetimeItem,
    PickerItem,
    PickerSchema,
    SelectItem,
    TimeItem,
)
from fast_tmp.amis.response import AmisStructError
from fast_tmp.responses import ListDataWithPage, TmpValueError

from .base import AbstractAmisAdminDB, AbstractControl, AmisOrm


class BaseAdminControl(AbstractAmisAdminDB, AbstractControl, AmisOrm):
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

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Column(type=ControlEnum.text, name=self.name, label=self.label)
        return self._column

    def get_control(self, request: Request) -> Control:
        if not self._control:
            self._control = Control(type=self._control_type, name=self.name, label=self.label)
            if not self._field.null:
                self._control.required = True
            if self._field.default is not None:
                self._control.value = self.orm_2_amis(self._field.default)
        return self._control

    def options(self):
        return None

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            column = self.get_column(request)
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
                    self._column_inline.quickEdit.clearable = True
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
        self._field.validate(self.amis_2_orm(value))


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

    def get_control(self, request: Request) -> Control:
        if not self._control:
            super().get_control(request)
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


class BooleanControl(IntEnumControl):
    _control_type = ControlEnum.select

    def options(self) -> List[str]:
        return ["True", "False"]

    def amis_2_orm(self, value: Any) -> Any:
        if (value == "None" or not value) and self._field.null:
            return None
        if value == "True":
            return True
        elif value == "False":
            return False
        raise TmpValueError(f"{self.label} 不能为 {value}")

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

    def get_control(self, request: Request) -> Control:
        if not self._control:
            super().get_control(request)
            self._control = DatetimeItem.from_orm(self._control)
        return self._control

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            super().get_column_inline(request)
            self._column_inline.quickEdit.format = "YYYY-MM-DD HH:mm:ss"
        return self._column_inline

    def amis_2_orm(self, value: Any) -> Any:
        if (value == "None" or not value) and self._field.null:
            return None
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    def orm_2_amis(self, value: datetime.datetime) -> Any:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


class DateControl(BaseAdminControl):
    _control_type = ControlEnum.date

    def get_control(self, request: Request) -> Control:
        if not self._control:
            super().get_control(request)
            self._control = DateItem.from_orm(self._control)
        return self._control

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            super().get_column_inline(request)
            self._column_inline.quickEdit.format = "YYYY-MM-DD"
        return self._column_inline

    def amis_2_orm(self, value: Any) -> Any:
        if (value == "None" or not value) and self._field.null:
            return None
        year, month, day = value.split("-")
        return datetime.date(int(year), int(month), int(day))

    def orm_2_amis(self, value: datetime.date) -> Any:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")


class TimeControl(BaseAdminControl):
    _control_type = ControlEnum.time

    def get_control(self, request: Request) -> Control:
        if not self._control:
            super().get_control(request)
            self._control = TimeItem.from_orm(self._control)
        return self._control

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            super().get_column_inline(request)
            self._column_inline.quickEdit.format = "HH:mm:ss"
            self._column_inline.quickEdit.inputFormat = "HH:mm:ss"
            self._column_inline.quickEdit.timeFormat = "HH:mm:ss"
        return self._column_inline

    def amis_2_orm(self, value: Any) -> Any:
        if not value:
            return None
        return datetime.time.fromisoformat(value)

    def orm_2_amis(self, value: datetime.date) -> Any:
        if value is None:
            return None
        return value.strftime("%H:%M:%S")


class JsonControl(TextControl):  # fixme 用代码编辑器重构？
    def amis_2_orm(self, value: Any) -> Any:
        return json.loads(value)

    def orm_2_amis(self, value: Any) -> Any:
        return json.dumps(value)

    def get_control(self, request: Request) -> Control:
        if not self._control:
            super().get_control(request)
            self._control.validations = "isJson"
        return self._control

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            super().get_column_inline(request)
            self._column_inline.quickEdit.validations = "isJson"
        return self._column_inline


class SelectByApi:
    """
    增加一个查询返回数据的接口
    """

    async def get_selects(
        self,
        request: Request,
        perPage: Optional[int],
        page: Optional[int],
    ) -> List[dict]:
        pass


class ForeignKeyPickerControl(BaseAdminControl, SelectByApi):  # todo 支持搜索功能
    """
    当外键太多的时候可以使用这个来进行查看，这样可以更容易选择数据
    """

    _control_type = ControlEnum.select

    async def get_selects(
        self,
        request: Request,
        perPage: Optional[int],
        page: Optional[int],
    ):
        field_model_all = self._field.related_model.all()
        if perPage is not None and page is not None:
            field_model = field_model_all.limit(perPage).offset(page - 1)
            count = await field_model_all.count()
            data = await field_model
            return ListDataWithPage(
                total=count,
                items=[{"pk": i.pk, "name": str(i)} for i in data],
            )
        else:
            data = await field_model_all
            return {"options": [{"pk": i.pk, "name": str(i)} for i in data]}

    def prefetch(self, request: Request, queryset: QuerySet) -> QuerySet:
        return queryset.select_related(self._field_name)

    def get_column_inline(self, request: Request) -> Column:
        raise AttributeError("foreignkey field can not be used in column inline.")

    def get_control(self, request: Request) -> Control:
        if not self._control:
            self._control = PickerItem(
                name=self.name,
                label=self.label,
                source=f"get:{self._prefix}/select/{self.name}",
                pickerSchema=PickerSchema(
                    name=self.name,
                    columns=[Column(label="pk", name="pk"), Column(label="name", name="name")],
                ),
                labelField="name",
                valueField="pk",
            )

            if self._field.null:
                self._control.clearable = True
        return self._control

    def orm_2_amis(self, value: Any) -> Any:
        return str(value)

    async def set_value(self, request: Request, obj: Model, value: Any):
        if value is not None:
            value = await self._field.related_model.filter(pk=value).first()
        setattr(obj, self._field_name, value)


class ForeignKeyControl(BaseAdminControl, SelectByApi):
    _control_type = ControlEnum.select

    async def get_selects(
        self,
        request: Request,
        perPage: Optional[int],
        page: Optional[int],
    ):
        field_model_all = self._field.related_model.all()
        if perPage is not None and page is not None:
            field_model = field_model_all.limit(perPage).offset(page - 1)
            count = await field_model_all.count()
            data = await field_model
            return ListDataWithPage(
                total=count,
                items=[{"pk": i.pk, "name": str(i)} for i in data],
            )
        else:
            data = await field_model_all
            return {"options": [{"pk": i.pk, "name": str(i)} for i in data]}

    def prefetch(self, request: Request, queryset: QuerySet) -> QuerySet:
        return queryset.select_related(self._field_name)

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Custom(
                label="作者",
                name=self.name,
                onMount=f"const text = document.createTextNode(value.label);dom.appendChild(text);${self.name}=value.pk;",
                onUpdate=f"const value=data.{self.name};dom.current.firstChild.textContent=value.label;${self.name}=value.pk;",
            )
        return self._column

    def get_column_inline(
        self, request: Request
    ) -> Column:  # fixme 需要特殊amis模块侧in鞥进行处理，以后学习一下前段看能不能自己写
        raise AttributeError("foreignkey field can not be used in column inline.")

    def get_control(self, request: Request) -> Control:
        if not self._control:
            self._control = SelectItem(
                name=self.name,
                label=self.label,
                source=f"get:{self._prefix}/select/{self.name}",
                labelField="name",
                valueField="pk",
            )
            if self._field.null:
                self._control.clearable = True
        return self._control

    def orm_2_amis(self, value: Any) -> Any:
        return {"label": str(value), "pk": value.pk}

    async def set_value(self, request: Request, obj: Model, value: Any):
        if value is not None:
            if isinstance(value, dict):
                value = value.get("pk")
            value = await self._field.related_model.filter(pk=value).first()
        setattr(obj, self._field_name, value)


def create_column(
    field_name: str,
    field_type: fields.Field,
    prefix: str,
):
    if isinstance(field_type, IntEnumFieldInstance):
        return IntEnumControl(field_name, field_type, prefix)
    elif isinstance(field_type, CharEnumFieldInstance):
        return StrEnumControl(field_name, field_type, prefix)
    elif isinstance(
        field_type, (fields.IntField, fields.SmallIntField, fields.BigIntField, fields.FloatField)
    ):
        return IntControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.TextField):
        return TextControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.DatetimeField):
        return DateTimeControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.DateField):
        return DateControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.CharField):
        return StrControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.BooleanField):
        return BooleanControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.JSONField):
        return JsonControl(field_name, field_type, prefix)
    elif isinstance(field_type, fields.TimeField):
        return TimeControl(field_name, field_type, prefix)
    elif isinstance(field_type, ForeignKeyFieldInstance):
        return ForeignKeyControl(field_name, field_type, prefix)
    else:
        raise AmisStructError("create_column error:", type(field_type))
