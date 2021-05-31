from typing import List, Optional, Type

from tortoise import Model, ManyToManyFieldInstance, BackwardFKRelation, ForeignKeyFieldInstance
from tortoise.fields import (
    BigIntField,
    BooleanField,
    CharField,
    DateField,
    DatetimeField,
    DecimalField,
    FloatField,
    IntField,
    JSONField,
    SmallIntField,
    TextField,
    TimeDeltaField,
    UUIDField,
)
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance

from fast_tmp.admin.schema.forms import Column, Mapping
from fast_tmp.admin.schema.forms.enums import FormWidgetSize, ItemModel
from fast_tmp.admin.schema.forms.widgets import (
    DateItem,
    DatetimeItem,
    NumberItem,
    SelectItem,
    SelectOption,
    SwitchItem,
    TextItem,
    TimeItem,
    UUIDItem, TransferItem, CheckboxesItem, PickerItem, SelectItemCanModifyItem,
)


def _get_base_attr(field_type, **kwargs) -> dict:
    res = dict(
        className=field_type.kwargs.get("className", None),
        inputClassName=field_type.kwargs.get("inputClassName", None),
        labelClassName=field_type.kwargs.get("labelClassName", None),
        name=field_type.model_field_name,
        label=field_type.kwargs.get("verbose_name", field_type.model_field_name),
        labelRemark=field_type.kwargs.get("labelRemark", None),
        description=field_type.kwargs.get("description", None),
        placeholder=field_type.kwargs.get("placeholder", "请输入..."),
        inline=field_type.kwargs.get("placeholder", False),
        submitOnChange=field_type.kwargs.get("submitOnChange", False),
        disabled=field_type.kwargs.get("disabled", False),
        disableOn=field_type.kwargs.get("disableOn", None),
        # validations=field_type.kwargs.get("validations", None),
        # validationErrors=field_type.kwargs.get("validationErrors", None),
        required=field_type.kwargs.get("required", True),
        mode=field_type.kwargs.get("mode", ItemModel.normal),
        size=field_type.kwargs.get("size", FormWidgetSize.md),
        value=getattr(field_type, "default", field_type.kwargs.get("default", None)),
    )
    res.update(kwargs)
    return res


def get_columns_from_model(
    model: Type[Model],
    include: List[str] = None,
    exclude: List[str] = None,
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    注意：多对多字段是无法显示的
    """
    fields = model._meta.fields_map

    res = []
    for field, field_type in fields.items():
        if include and field not in include or exclude and field in exclude:
            continue
        if isinstance(field_type, (IntEnumFieldInstance, CharEnumFieldInstance)):
            res.append(
                Mapping(
                    name=field, label=field_type.kwargs.get("verbose_name", field),
                    map={
                        k: v for k, v in field_type.enum_type.choices.items()
                    }
                )
            )
            # fixme:处理开关字段
        # elif isinstance(field_type,):#fixme:处理特殊字段，比如json字段，或者图片、开关等需要特殊显示的类型。
        elif isinstance(field_type, ManyToManyFieldInstance):
            continue
        else:
            res.append(
                Column(
                    name=field, label=field_type.kwargs.get("verbose_name", field)
                )
            )
    return res


# fixme:增加对所有输入参数进行排序并hash存储，如果调用过则读取缓存


def get_controls_from_model(
    model: Type[Model],
    include: List[str] = None,
    exclude: List[str] = None,
    extra_fields: Optional[List[Column]] = None,
    exclude_readonly: bool = False,
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    extra_field:额外的自定义字段
    """
    fields = model._meta.fields_map
    res = []
    for field, field_type in fields.items():
        if include and field not in include or exclude and field in exclude:
            continue
        if exclude_readonly and field_type.pk:
            continue
        if isinstance(field_type, (IntField, SmallIntField, BigIntField)):
            if isinstance(field_type, IntEnumFieldInstance):
                enum_type = field_type.enum_type
                res.append(
                    SelectItem(
                        options=[
                            SelectOption(label=label, value=value)
                            for value, label in enum_type.choices.items()
                        ],
                        **_get_base_attr(field_type),
                    ),
                )
            else:
                res.append(
                    NumberItem(
                        min=field_type.kwargs.get("min", None)
                            or field_type.constraints.get("ge"),
                        max=field_type.kwargs.get("max", None)
                            or field_type.constraints.get("le"),
                        precision=field_type.kwargs.get("precision", 0),
                        step=field_type.kwargs.get("step", 1),
                        **_get_base_attr(field_type),
                        validations={
                            "minimum": field_type.kwargs.get("min", None)
                                       or field_type.constraints.get("ge"),
                            "maximum": field_type.kwargs.get("max", None)
                                       or field_type.constraints.get("le"),
                        },
                    ),
                )
        elif isinstance(field_type, CharField):
            if isinstance(field_type, CharEnumFieldInstance):
                enum_type = field_type.enum_type
                res.append(
                    SelectItem(
                        options=[
                            SelectOption(label=label, value=value)
                            for value, label in enum_type.choices.items()
                        ],
                        **_get_base_attr(field_type),
                    ),
                )
            else:
                res.append(
                    TextItem(
                        **_get_base_attr(field_type),
                        validations={
                            "maxLength": field_type.kwargs.get("maxLength", None)
                                         or field_type.max_length,
                        },
                    )
                )
        # todo:等待完成,另，需要完成date
        elif isinstance(field_type, DatetimeField):
            res.append(
                DatetimeItem(
                    **_get_base_attr(field_type),
                    format=field_type.kwargs.get("format", "YYYY-MM-DD HH:mm:ss"),
                    inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD HH:mm:ss"),
                )
            )
        elif isinstance(field_type, DateField):
            res.append(
                DateItem(
                    **_get_base_attr(field_type),
                    format=field_type.kwargs.get("format", "YYYY-MM-DD"),
                    inputFormat=field_type.kwargs.get("inputFormat", "YYYY-MM-DD"),
                )
            )
        elif isinstance(field_type, TimeDeltaField):
            res.append(
                TimeItem(
                    **_get_base_attr(field_type),
                    format=field_type.kwargs.get("format", "HH:mm"),
                    inputFormat=field_type.kwargs.get("inputFormat", "HH:mm"),
                    # placeholder=field_type.kwargs.get('placeholder', "请选择时间"),
                    timeConstrainst=field_type.kwargs.get("timeConstrainst", False),
                )
            )
        elif isinstance(field_type, CharEnumFieldInstance):  # fixme:需要修复
            print(field_type.enum_type)
        elif isinstance(field_type, BooleanField):
            res.append(
                SwitchItem(
                    type="switch",
                    # **_get_base_attr(field_type),
                    name=field_type.model_field_name,
                    label="开关",
                    trueValue=field_type.kwargs.get("trueValue", True),
                    falseValue=field_type.kwargs.get("falseValue", False),
                )
            )
        elif isinstance(field_type, FloatField):
            validation = {}
            if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
                validation["minimum"] = field_type.kwargs.get(
                    "min", None
                ) or field_type.constraints.get("ge")
            if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
                validation["maximum"] = field_type.kwargs.get(
                    "max", None
                ) or field_type.constraints.get("le")
            res.append(
                NumberItem(
                    min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
                    max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
                    precision=field_type.kwargs.get("precision", None),
                    step=field_type.kwargs.get("step", 1),
                    showSteps=field_type.kwargs.get("showSteps", None),
                    **_get_base_attr(field_type),
                    validations=validation,
                )
            )
        elif isinstance(field_type, DecimalField):
            validation = {}
            if field_type.kwargs.get("min", None) or field_type.constraints.get("ge"):
                validation["minimum"] = field_type.kwargs.get(
                    "min", None
                ) or field_type.constraints.get("ge")
            if field_type.kwargs.get("max", None) or field_type.constraints.get("le"):
                validation["maximum"] = field_type.kwargs.get(
                    "max", None
                ) or field_type.constraints.get("le")
            res.append(
                NumberItem(
                    min=field_type.kwargs.get("min", None) or field_type.constraints.get("ge"),
                    max=field_type.kwargs.get("max", None) or field_type.constraints.get("le"),
                    precision=field_type.kwargs.get("precision", 2),
                    step=field_type.kwargs.get("step", 1),
                    showSteps=field_type.kwargs.get("showSteps", None),
                    **_get_base_attr(field_type),
                    validations=validation,
                )
            )
        elif isinstance(field_type, JSONField):  # fixme:需要解决tortoise-orm字段问题
            pass
        elif isinstance(field_type, TextField):
            res.append(
                TextItem(
                    **_get_base_attr(field_type),
                )
            )
        elif isinstance(field_type, UUIDField):
            res.append(
                UUIDItem(
                    **_get_base_attr(field_type), length=field_type.kwargs.get("length", None)
                )
            )
        elif isinstance(field_type, ManyToManyFieldInstance):  # 多对多字段
            res.append(
                SelectItem(
                    **_get_base_attr(field_type, required=False),
                    source=f"get:/{field_type.model_field_name}-selects",
                    multiple=True,
                    extractValue=True,
                    joinValues=False,
                )
            )
        elif isinstance(field_type, BackwardFKRelation):
            res.append(
                SelectItem(
                    **_get_base_attr(field_type, required=False),
                    source=f'get:/{field_type.model_field_name}-selects',
                )
            )
        elif isinstance(field_type, ForeignKeyFieldInstance):
            res.append(
                SelectItem(
                    **_get_base_attr(field_type, required=False),
                    source=f'get:/{field_type.model_field_name}-selects',
                )
            )
        else:
            raise ValueError(f"{field}字段的字段类型尚不支持!")
    if extra_fields:
        res.extend(extra_fields)
    return res