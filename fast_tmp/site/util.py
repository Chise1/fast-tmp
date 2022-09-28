import datetime
import json
from typing import Any, Coroutine, List, Optional

from starlette.requests import Request
from tortoise import ForeignKeyFieldInstance, ManyToManyFieldInstance, Model, fields
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance

from fast_tmp.amis.custom import Custom
from fast_tmp.amis.forms import Column, ColumnInline, Control, ControlEnum, QuickEdit
from fast_tmp.amis.forms.widgets import (
    DateItem,
    DatetimeItem,
    PickerItem,
    PickerSchema,
    SelectItem,
    TimeItem,
    TransferItem,
)
from fast_tmp.amis.response import AmisStructError
from fast_tmp.responses import ListDataWithPage, TmpValueError

from ..amis.actions import DialogAction
from ..amis.buttons import Operation
from ..amis.crud import CRUD
from ..amis.frame import Dialog
from .base import AbstractAmisAdminDB, AbstractControl, AmisOrm


class BaseAdminControl(AbstractAmisAdminDB, AbstractControl, AmisOrm):
    """
    默认的将model字段转control的类
    """

    label: str
    _field: fields.Field
    _control: Control = None  # type: ignore
    _column: Column = None  # type: ignore
    _column_inline: ColumnInline = None  # type: ignore
    _control_type: ControlEnum = ControlEnum.input_text
    _many = False  # 多对多字段标记，查询的时候默认跳过

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Column(name=self.name, label=self.label)
        return self._column

    def get_control(self, request: Request) -> Control:
        if not self._control:
            self._control = Control(type=self._control_type, name=self.name, label=self.label)
            if not self._field.null:  # type: ignore
                self._control.required = True
            if self._field.default is not None:  # type: ignore
                self._control.value = self.orm_2_amis(self._field.default)  # type: ignore
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
                if self._field.null:  # type: ignore
                    self._column_inline.quickEdit.clearable = True
        return self._column_inline

    async def set_value(self, request: Request, obj: Model, value: Any):
        value = await self.validate(value)
        setattr(obj, self.name, value)

    async def get_value(self, request: Request, obj: Model) -> Any:
        return self.orm_2_amis(getattr(obj, self.name))

    def __init__(self, name: str, field: fields.Field, prefix: str, **kwargs):
        super().__init__(name, prefix, **kwargs)
        self._field = field  # type: ignore
        self.name = name
        self.label = kwargs.get("label") or self.name

    async def validate(self, value: Any) -> Any:
        value = self.amis_2_orm(value)
        self._field.validate(value)  # type: ignore
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

    def get_control(self, request: Request) -> Control:
        if not self._control:
            super().get_control(request)
            d = self._control.dict(exclude_none=True)
            d.pop("type")
            if self._field.null:  # type: ignore
                d["clearable"] = True
            self._control = SelectItem(**d)
            self._control.options = self.options()
        return self._control

    def orm_2_amis(self, value: Any) -> Any:
        if value is not None:
            return value.name

    def amis_2_orm(self, value: Any) -> Any:
        if value is None and self._field.null:  # type: ignore
            return None
        for i in self._field.enum_type:  # type: ignore
            if i.name == value:
                return i.value
        raise TmpValueError(f"{self.label} 不能为 {value}")

    def options(self) -> List[str]:
        res = []
        for i in self._field.enum_type:  # type: ignore
            res.append(i.name)
        return res


class BooleanControl(IntEnumControl):
    _control_type = ControlEnum.select

    def options(self) -> List[str]:
        return ["True", "False"]

    async def validate(self, value: Any) -> Any:
        return self.amis_2_orm(value)

    def amis_2_orm(self, value: Any) -> Any:
        if (value == "None" or not value) and self._field.null:  # type: ignore
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
        if (value == "None" or not value) and self._field.null:  # type: ignore
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
        if (value == "None" or not value) and self._field.null:  # type: ignore
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

    def orm_2_amis(self, value: datetime.time) -> Any:
        if value is None:
            return None
        if callable(value):
            return value().strftime("%H:%M:%S")
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


class RelationSelectApi:
    """
    增加一个查询foreign外键所有字段的接口
    """

    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
    ) -> List[dict]:
        pass


class ForeignKeyPickerControl(BaseAdminControl, RelationSelectApi):  # todo 支持搜索功能
    """
    当外键太多的时候可以使用这个来进行查看，这样可以更容易选择数据
    """

    _control_type = ControlEnum.select
    _field: fields.ForeignKeyRelation

    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
    ):
        field_model_all = self._field.related_model.all()  # type: ignore
        if perPage is not None and page is not None:
            field_model = field_model_all.limit(perPage).offset((page - 1) * perPage)
            count = await field_model_all.count()
            data = await field_model
            return ListDataWithPage(
                total=count,
                items=[{"value": i.pk, "label": str(i)} for i in data],
            )
        else:
            data = await field_model_all
            return {"options": [{"value": i.pk, "label": str(i)} for i in data]}

    def prefetch(self) -> Optional[str]:
        return "select"

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
                    columns=[
                        Column(label="label", name="label"),
                        Column(label="value", name="value"),
                    ],
                ),
                labelField="label",
                valueField="value",
            )

            if self._field.null:  # type: ignore
                self._control.clearable = True
        return self._control

    def orm_2_amis(self, value: Any) -> Any:
        return str(value)

    async def validate(self, value: Any) -> Any:
        if value is not None:
            return await self._field.related_model.filter(pk=value).first()  # type: ignore

    async def set_value(self, request: Request, obj: Model, value: Any):
        value = await self.validate(value)
        setattr(obj, self.name, value)


class ForeignKeyControl(BaseAdminControl, RelationSelectApi):
    _control_type = ControlEnum.select

    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
    ):
        field_model_all = self._field.related_model.all()  # type: ignore
        if perPage is not None and page is not None:
            field_model = field_model_all.limit(perPage).offset((page - 1) * perPage)
            count = await field_model_all.count()
            data = await field_model
            return ListDataWithPage(
                total=count,
                items=[{"value": i.pk, "label": str(i)} for i in data],
            )
        else:
            data = await field_model_all
            return {"options": [{"value": i.pk, "label": str(i)} for i in data]}

    def prefetch(self) -> Optional[str]:
        return "select"

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Custom(
                label="作者",
                name=self.name,
                onMount=f"const text = document.createTextNode(value.label);dom.appendChild(text);${self.name}=value.value;",
                onUpdate=f"const value=data.{self.name};dom.current.firstChild.textContent=value.label;${self.name}=value.value;",
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
                labelField="label",
                valueField="value",
            )
            if self._field.null:  # type: ignore
                self._control.clearable = True
        return self._control

    def orm_2_amis(self, value: Any) -> Any:
        return {"label": str(value), "value": value.pk}

    async def set_value(self, request: Request, obj: Model, value: Any):
        if value is not None:
            if isinstance(value, dict):
                value = value.get("value")
            value = await self._field.related_model.filter(pk=value).first()  # type: ignore
        setattr(obj, self.name, value)


class ManyToManyControl(BaseAdminControl, RelationSelectApi):
    _many = True
    _control_type = ControlEnum.select

    def prefetch(self) -> Optional[str]:
        return "prefetch"

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Operation(
                label=self.name,
                buttons=[
                    DialogAction(
                        label="查看",
                        dialog=Dialog(
                            title=self.label,
                            body=CRUD(
                                api="get:"
                                + self._field.model.__name__  # type: ignore
                                + f"/select/{self.name}?pk=$pk",
                                columns=[
                                    Column(label="pk", name="pk"),
                                    Column(label="label", name="label"),
                                ],
                            ),
                        ),
                    )
                ],
            )
        return self._column

    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
    ):
        related_model = self._field.related_model  # type: ignore
        if pk is not None:
            queryset = related_model.filter(**{self._field.related_name: pk})  # type: ignore
        else:
            queryset = related_model.all()
        if pk is not None:
            count = await queryset.count()
            data = await queryset
            return ListDataWithPage(
                total=count,
                items=[{"value": i.pk, "label": str(i)} for i in data],
            )
        else:
            data = await queryset
            return {"options": [{"value": i.pk, "label": str(i)} for i in data]}

    def get_control(self, request: Request) -> Control:
        if not self._control:
            self._control = TransferItem(
                name=self.name,
                label=self.label,
                source=f"get:{self._prefix}/select/{self.name}",
            )
            if self._field.null:  # type: ignore
                self._control.clearable = True
        return self._control

    def amis_2_orm(self, value: List[dict]) -> Any:
        if isinstance(value, str):
            return value.split(",")
        return [i["value"] for i in value]

    async def validate(self, value: Any) -> Any:
        if value is not None:
            pks = self.amis_2_orm(value)
            if len(pks) > 0:
                return await self._field.related_model.filter(pk__in=pks)  # type: ignore
        return []

    async def set_value(self, request: Request, obj: Model, value: Any) -> Optional[Coroutine]:
        value = await self.validate(value)
        field: fields.ManyToManyRelation = getattr(obj, self.name)
        if obj.pk is None and value:  # create
            return field.add(*value)
        add_field = []
        remove_field = []
        for i in field:
            for j in value:
                if j.pk == i.pk:
                    break
            else:
                remove_field.append(i)
        for j in value:
            for i in field:
                if j.pk == i.pk:
                    break
            else:
                add_field.append(j)
        if len(remove_field) > 0:
            await field.remove(*remove_field)
        if len(add_field) > 0:
            await field.add(*add_field)
        return None

    def get_column_inline(
        self, request: Request
    ) -> Column:  # fixme 需要特殊amis模块侧in鞥进行处理，以后学习一下前段看能不能自己写
        raise AttributeError("manytomany field can not be used in column inline.")

    def orm_2_amis(self, value: Any) -> Any:
        return [{"label": str(i), "value": i.pk} for i in value]


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
    elif isinstance(field_type, ManyToManyFieldInstance):
        return ManyToManyControl(field_name, field_type, prefix)
    else:
        raise AmisStructError("create_column error:", type(field_type))
