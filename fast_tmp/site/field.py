import datetime
import json
from abc import abstractmethod
from decimal import Decimal
from typing import Any, Coroutine, Iterable, List, Optional, Tuple

from starlette.requests import Request
from tortoise import (
    BackwardFKRelation,
    BackwardOneToOneRelation,
    ForeignKeyFieldInstance,
    ManyToManyFieldInstance,
    Model,
    OneToOneFieldInstance,
    fields,
)
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance

from fast_tmp.amis.actions import DialogAction
from fast_tmp.amis.column import Column, Operation
from fast_tmp.amis.crud import CRUD
from fast_tmp.amis.formitem import (
    Custom,
    DateItem,
    DatetimeItem,
    FileItem,
    FormItem,
    FormItemEnum,
    ImageItem,
    NumberItem,
    RichTextItem,
    SelectItem,
    TimeItem,
    TransferItem,
)
from fast_tmp.amis.frame import Dialog
from fast_tmp.amis.response import AmisStructError
from fast_tmp.contrib.auth.hashers import make_password
from fast_tmp.contrib.tortoise.fields import FileField, ImageField, RichTextField
from fast_tmp.exceptions import TmpValueError
from fast_tmp.responses import ListDataWithPage
from fast_tmp.site.base import BaseAdminControl, BaseControl
from fast_tmp.utils import add_media_start, remove_media_start


class PkControl(BaseAdminControl):
    """
    主键
    """


class StrControl(BaseAdminControl):
    """
    基础的字符串control
    """


class TextControl(StrControl):
    _control_type = FormItemEnum.textarea


class IntControl(BaseAdminControl):
    _control_type = FormItemEnum.input_number


class DecimalControl(BaseAdminControl):
    """
    amis并没有decimal，所以这里只能使用浮点数
    建议使用int来替换dec，比如按照分来计算之类的
    """

    _control_type = FormItemEnum.input_number

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            self._control = NumberItem(
                type=self._control_type, name=self.name, label=self.label, big=True
            )
            self._control.precision = self._field.decimal_places
            self._control.max = self._field.max_digits * 9
            if not self._field.null:
                self._control.required = True
            if self._field.default is not None:
                self._control.value = self.orm_2_amis(self._field.default)
        return self._control

    def amis_2_orm(self, value: float) -> Any:
        if value is not None:
            return Decimal(value)

    def orm_2_amis(self, value: Decimal) -> Any:
        if value is not None:
            return float(value)


class IntEnumControl(BaseAdminControl):
    _control_type = FormItemEnum.select

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            super().get_formitem(request, codenames)
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
    _control_type = FormItemEnum.select

    def options(self) -> List[str]:
        return ["True", "False"]

    def amis_2_orm(self, value: Any) -> Any:
        if not value and self._field.null:
            return None
        if value == "True":
            return True
        elif value == "False":
            return False
        raise TmpValueError(f"{self.label} 不能为 {value}")

    def orm_2_amis(self, value: Any) -> Any:
        if value is None:
            return
        elif value:
            return "True"
        return "False"


class StrEnumControl(IntEnumControl):
    pass


class DateTimeControl(BaseAdminControl):
    _control_type = FormItemEnum.input_datetime

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            super().get_formitem(request, codenames)
            self._control = DatetimeItem.from_orm(self._control)
        return self._control

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            super().get_column_inline(request)
            self._column_inline.quickEdit.format = "YYYY-MM-DD HH:mm:ss"
        return self._column_inline

    def amis_2_orm(self, value: str) -> Any:
        if value:
            return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        if self._field.null:
            return None
        raise TmpValueError(f"{self.label} 不能为 {value}")

    def orm_2_amis(self, value: datetime.datetime) -> Any:
        if value is not None:
            return value.strftime("%Y-%m-%d %H:%M:%S")


class DateControl(BaseAdminControl):
    _control_type = FormItemEnum.input_date

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            super().get_formitem(request, codenames)
            self._control = DateItem.from_orm(self._control)
        return self._control

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            super().get_column_inline(request)
            self._column_inline.quickEdit.format = "YYYY-MM-DD"
        return self._column_inline

    def amis_2_orm(self, value: Any) -> Any:
        if value:
            year, month, day = value.split("-")
            return datetime.date(int(year), int(month), int(day))
        if self._field.null:
            return None
        raise TmpValueError(f"{self.label} 不能为 {value}")

    def orm_2_amis(self, value: datetime.date) -> Any:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")


class TimeControl(BaseAdminControl):
    _control_type = FormItemEnum.input_time

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            super().get_formitem(request, codenames)
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
        if value:
            return datetime.time.fromisoformat(value)
        if self._field.null:
            return None
        raise TmpValueError(f"{self.label} 不能为 {value}")

    def orm_2_amis(self, value: Optional[datetime.time]) -> Any:
        if value is not None:
            return value.strftime("%H:%M:%S")


class JsonControl(TextControl):
    def amis_2_orm(self, value: Any) -> Any:
        if not value:
            return None
        return json.loads(value)

    def orm_2_amis(self, value: Any) -> Any:
        return json.dumps(value)

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            super().get_formitem(request, codenames)
            self._control.validations = "isJson"
            if not callable(self._field.default):
                self._control.required = True  # jsonfield不能为空不然写数据库必爆炸
                if not self._control.value:  # 如果有默认值则已经在父类里面被调用
                    self._control.value = "{}"
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

    @abstractmethod
    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
        filter: Any = None,  # todo 考虑支持页面选项搜索
    ) -> List[dict]:
        """
        多对多或多对一的时候，用于选择项的读取
        """


class ForeignKeyControl(BaseAdminControl, RelationSelectApi):
    _control_type = FormItemEnum.select
    need_perms: Optional[Tuple[str, ...]] = None
    _control: SelectItem = None  # type: ignore

    def related_prefix(self) -> str:
        # todo: 增加到文档，创建按钮根据页面注册的类的prefix进行搜索。
        return self.field.related_model.__name__.lower()

    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
        filter: Any = None,
    ):
        field_model_all = self._field.related_model.all()
        # if filter:
        #     if isinstance(filter, dict):
        #         field_model_all = self._field.related_model.filter(**filter)
        #     else:
        #         field_model_all = self._field.related_model.filter(filter)
        # if perPage is not None and page is not None:
        #     field_model = field_model_all.limit(perPage).offset((page - 1) * perPage)
        #     count = await field_model_all.count()
        #     data = await field_model
        #     return ListDataWithPage(
        #         total=count,
        #         items=[{"value": i.pk, "label": str(i)} for i in data],
        #     )
        # else:
        data = await field_model_all
        return {"options": [{"value": i.pk, "label": str(i)} for i in data]}

    def prefetch(self) -> Optional[str]:
        return "select"

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Custom(
                label=self.name,
                name=self.name,
                onMount=f"const text = document.createTextNode(value.label);dom.appendChild(text);${self.name}=value.value;",
                onUpdate=f"const value=data.{self.name};dom.current.firstChild.textContent=value.label;${self.name}=value.value;",
            )
        return self._column

    def get_column_inline(self, request: Request) -> Column:
        raise AttributeError("foreignkey field can not be used in column inline.")

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        from fast_tmp.site import resources

        if not self._control:
            self._control = SelectItem(
                name=self.name,
                label=self.label,
                source=f"get:{self.prefix}/select/{self.name}",
                labelField="label",
                valueField="value",
                clearable=True,
            )
            if not self._field.null:
                self._control.required = True
            else:
                self._control.clearable = True
        if self.need_perms:
            perm = self.need_perms[0]
            if perm in codenames:
                prefix = self._field.related_model.__name__.lower()
                for model_prefix, model in resources.items():
                    if prefix == model_prefix:
                        controls = model.get_create_controls(request, codenames)
                        self._control.creatable = True
                        self._control.createBtnLabel = "新增"
                        self._control.addControls = controls
                        self._control.addApi = model.prefix + "/create"
                        break
        return self._control

    def orm_2_amis(self, value: Any) -> Any:
        if not value:
            return {"label": "-", "value": None}
        return {"label": str(value), "value": value.pk}

    async def set_value(self, request: Request, obj: Model, value: Any):
        if value is not None:
            if isinstance(value, dict):
                value = value.get("value")
            value = await self._field.related_model.filter(pk=value).first()
        setattr(obj, self.name, value)

    def need_codenames(self, request: Request) -> Tuple[str, ...]:
        """
        判断，如果用户有对应页面的创建权限，则可以为该表增加创建按钮
        """
        if self.need_perms is None:
            self.need_perms = (self.related_prefix() + "_create",)
        return self.need_perms


# 如果是可选，怎么过滤的问题？反向过滤？
class OneToOneControl(ForeignKeyControl):
    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
        filter: Any = None,
    ):
        exist_pks = await self.field.model.all().values(self.field.source_field)
        field_model_all = self.field.related_model.filter(
            **{self.field.to_field + "__not_in": [i[self.field.source_field] for i in exist_pks]}
        )
        data = await field_model_all
        return {"options": [{"value": i.pk, "label": str(i)} for i in data]}

    def get_column_inline(self, request: Request) -> Column:
        # todo 一对一可以使用inline
        raise AttributeError("foreignkey field can not be used in column inline.")


class ManyToManyControl(BaseAdminControl, RelationSelectApi):
    _many = True
    _control_type = FormItemEnum.select

    def prefetch(self) -> Optional[str]:
        return "prefetch"

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Operation(
                label=self.label,
                buttons=[
                    DialogAction(
                        label="查看",
                        dialog=Dialog(
                            title=self.label,
                            body=CRUD(
                                api=f"get:{self.prefix}/select/{self.name}?pk=$pk",
                                columns=[
                                    Column(label="主键", name="pk"),
                                    Column(label="名称", name="label"),
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
        filter: Any = None,
    ):
        related_model = self._field.related_model
        if pk is not None:
            queryset = related_model.filter(**{self._field.related_name: pk})
        else:
            queryset = related_model.all()
        # if filter:
        #     if isinstance(filter, dict):
        #         queryset = queryset.filter(**filter)
        #     else:
        #         queryset = queryset(filter)
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

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            self._control = TransferItem(
                name=self.name,
                label=self.label,
                source=f"get:{self.prefix}/select/{self.name}",
            )
            if self._field.null:
                self._control.clearable = True
        return self._control

    def amis_2_orm(self, value: List[dict]) -> Any:
        if isinstance(value, str):
            return value.split(",")
        return [i["value"] for i in value]

    async def validate(self, value: Any, is_create=False) -> Any:
        if value is not None:
            pks = self.amis_2_orm(value)
            if len(pks) > 0:
                return await self._field.related_model.filter(pk__in=pks)
        return []

    async def set_value(self, request: Request, obj: Model, value: Any) -> Optional[Coroutine]:
        value = await self.validate(value)
        field: fields.ManyToManyRelation = getattr(obj, self.name)
        if obj.pk is None:
            if value:  # create
                return field.add(*value)
            return None
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

    def get_column_inline(self, request: Request) -> Column:
        raise AttributeError("manytomany field can not be used in column inline.")

    def orm_2_amis(self, value: Any) -> Any:
        return [{"label": str(i), "value": i.pk} for i in value]


# todo 增加创建按钮?
class BackwardFKControl(ManyToManyControl):
    _many = True
    _control_type = FormItemEnum.select

    def prefetch(self) -> Optional[str]:
        return "prefetch"

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Operation(
                label=self.label,
                buttons=[
                    DialogAction(
                        label="查看",
                        dialog=Dialog(
                            title=self.label,
                            body=CRUD(
                                api=f"get:{self.prefix}/select/{self.name}?pk=$pk",
                                columns=[
                                    Column(label="主键", name="pk"),
                                    Column(label="名称", name="label"),
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
        filter: Any = None,
    ):
        related_model = self._field.related_model
        if pk is not None:
            queryset = related_model.filter(**{self._field.related_name: pk})
        else:
            queryset = related_model.all()
        # if filter:
        #     if isinstance(filter, dict):
        #         queryset = queryset.filter(**filter)
        #     else:
        #         queryset = queryset(filter)
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

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        raise AttributeError(f"BackwardFKControl field {self.name} can not be created")

    def get_column_inline(self, request: Request) -> Column:
        raise AttributeError(
            f"BackwardFKControl field {self.name} can not be used in column inline."
        )

    def orm_2_amis(self, value: Any) -> Any:
        return [{"label": str(i), "value": i.pk} for i in value]


class BackwardOneToOneControl(OneToOneControl):
    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Custom(
                label=self.name,
                name=self.name,
                onMount=f"const text = document.createTextNode(value.label);dom.appendChild(text);${self.name}=value.value;",
                onUpdate=f"const value=data.{self.name};dom.current.firstChild.textContent=value.label;${self.name}=value.value;",
            )
        return self._column

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            self._control = SelectItem(
                name=self.name,
                label=self.label,
                source=f"get:{self.prefix}/select/{self.name}",
                labelField="label",
                valueField="value",
                clearable=True,
            )
        return self._control

    def need_codenames(self, request: Request) -> Tuple[str, ...]:
        """
        判断，如果用户有对应页面的创建权限，则可以为该表增加创建按钮
        """
        if self.need_perms is None:
            self.need_perms = (self.related_prefix() + "_create",)
        return self.need_perms

    async def get_selects(
        self,
        request: Request,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
        filter: Any = None,
    ):
        field_model_all = self.field.related_model.filter(**{self.field.relation_field: None})
        # if filter:
        #     if isinstance(filter, dict):
        #         field_model_all = self._field.related_model.filter(**filter)
        #     else:
        #         field_model_all = self._field.related_model.filter(filter)
        # if perPage is not None and page is not None:
        #     field_model = field_model_all.limit(perPage).offset((page - 1) * perPage)
        #     count = await field_model_all.count()
        #     data = await field_model
        #     return ListDataWithPage(
        #         total=count,
        #         items=[{"value": i.pk, "label": str(i)} for i in data],
        #     )
        # else:
        data = await field_model_all
        return {"options": [{"value": i.pk, "label": str(i)} for i in data]}

    async def set_value(self, request: Request, obj: Model, value: Any):
        """
        一对一不允许修改
        """
        pass


class FileControl(BaseAdminControl):
    _control_type = FormItemEnum.input_file
    prefix = ""

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            self._control = FileItem(
                name=self.name,
                label=self.label,
                receiver=f"{self.prefix}/file/{self.name}",
            )
            if not self._field.null:
                self._control.required = True
            if self._field.default is not None:
                self._control.value = self.orm_2_amis(self._field.default)
        return self._control

    def orm_2_amis(self, value: str) -> Any:
        if value is not None:
            return add_media_start(value)

    def amis_2_orm(self, value: Any) -> Any:
        if value is not None:
            return remove_media_start(value)


class ImageControl(BaseAdminControl):
    _control_type = FormItemEnum.input_image
    prefix = ""

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            self._control = ImageItem(
                name=self.name,
                label=self.label,
                receiver=f"{self.prefix}/file/{self.name}",
            )
            if not self._field.null:
                self._control.required = True
            if self._field.default is not None:
                self._control.value = self.orm_2_amis(self._field.default)
        return self._control

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Column(type="image", name=self.name, label=self.label)
        return self._column

    def orm_2_amis(self, value: str) -> Any:
        if value is not None:
            return add_media_start(value)

    def amis_2_orm(self, value: Any) -> Any:
        if value is not None:
            return remove_media_start(value)


class RichTextControl(BaseAdminControl):
    _control_type = FormItemEnum.input_rich_text

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            self._control = RichTextItem(type=self._control_type, name=self.name, label=self.label)
            if not self._field.null:
                self._control.required = True
            if self._field.default is not None:
                self._control.value = self.orm_2_amis(self._field.default)
        return self._control


def create_column(
    field_name: str,
    field_type: fields.Field,
    prefix: str,
):
    if isinstance(field_type, IntEnumFieldInstance):
        return IntEnumControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, CharEnumFieldInstance):
        return StrEnumControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(
        field_type, (fields.IntField, fields.SmallIntField, fields.BigIntField, fields.FloatField)
    ):
        return IntControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, fields.TextField):
        return TextControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, fields.DatetimeField):
        return DateTimeControl(
            "", field_name, field_type.null, field_type.default, field=field_type
        )
    elif isinstance(field_type, fields.DateField):
        return DateControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, fields.CharField):
        return StrControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, fields.BooleanField):
        return BooleanControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, fields.JSONField):
        return JsonControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, fields.TimeField):
        return TimeControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, ManyToManyFieldInstance):
        return ManyToManyControl(
            "", field_name, field_type.null, field_type.default, field=field_type, prefix=prefix
        )
    elif isinstance(field_type, OneToOneFieldInstance):
        return OneToOneControl(
            "", field_name, field_type.null, field_type.default, field=field_type, prefix=prefix
        )
    elif isinstance(field_type, ForeignKeyFieldInstance):
        return ForeignKeyControl(
            "", field_name, field_type.null, field_type.default, field=field_type, prefix=prefix
        )
    elif isinstance(field_type, BackwardOneToOneRelation):
        return BackwardOneToOneControl(
            "", field_name, field_type.null, field_type.default, field=field_type, prefix=prefix
        )
    elif isinstance(field_type, BackwardFKRelation):  # 多对一反向
        return BackwardFKControl(
            "", field_name, field_type.null, field_type.default, field=field_type, prefix=prefix
        )

    elif isinstance(field_type, ImageField):
        return ImageControl(
            "", field_name, field_type.null, field_type.default, field=field_type, prefix=prefix
        )
    elif isinstance(field_type, RichTextField):
        return RichTextControl(
            "", field_name, field_type.null, field_type.default, field=field_type
        )
    elif isinstance(field_type, FileField):
        return FileControl("", field_name, field_type.null, field_type.default, field=field_type)
    elif isinstance(field_type, fields.DecimalField):
        return DecimalControl("", field_name, field_type.null, field_type.default, field=field_type)
    else:
        raise AmisStructError("create_column error:", type(field_type))


# fixme 以后考虑创建更新的control分离?
class Password(BaseControl):
    _control_type = FormItemEnum.input_password

    async def get_value(self, request: Request, obj: Model) -> Any:
        return None

    async def set_value(self, request: Request, obj: Model, value: Any):
        if obj.pk is not None:
            old_password = getattr(obj, self.name)
            if value and value != old_password and len(value) > 0:
                setattr(obj, self.name, make_password(value))
        else:
            if not value:
                raise TmpValueError("password can not be none.")
            await super().set_value(request, obj, make_password(value))

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        if not self._control:
            self._control = FormItem(type=self._control_type, name=self.name, label=self.label)
            if not self.null:
                if self.default is not None:
                    self._control.value = self.orm_2_amis(self.default)
        return self._control
