from enum import Enum
from typing import List, Optional, Tuple, Type, Union
from logging import getLogger
from tortoise import BackwardFKRelation, ForeignKeyFieldInstance, ManyToManyFieldInstance, Model
from tortoise.fields import (
    BigIntField,
    BooleanField,
    CharField,
    DateField,
    DatetimeField,
    DecimalField,
    Field,
    FloatField,
    IntField,
    JSONField,
    SmallIntField,
    TextField,
    TimeDeltaField,
    UUIDField,
)
from tortoise.fields.data import CharEnumFieldInstance, IntEnumFieldInstance

from fast_tmp.amis.actions import DialogAction
from fast_tmp.amis.forms import Column, Mapping
from fast_tmp.amis.forms.enums import FormWidgetSize, ItemModel
from fast_tmp.amis.forms.widgets import (
    DateItem,
    DatetimeItem,
    NumberItem,
    SelectItem,
    SelectOption,
    SwitchItem,
    TextItem,
    TimeItem,
    UUIDItem,
)

from fast_tmp.amis.forms import Column as AmisColumn
from fast_tmp.amis.forms import Column as FormColumn

logger = getLogger(__file__)


def _get_base_attr(field_type: Field, **kwargs) -> dict:
    res = dict(
        className=None,
        inputClassName=None,
        labelClassName=None,
        name=field_type.model_field_name,
        label=field_type.model_field_name,
        labelRemark=None,
        description=None,
        placeholder=None,
        inline=False,
        submitOnChange=False,
        disabled=False,
        disableOn=None,
        required=field_type.required,
        mode=ItemModel.normal,
        size=FormWidgetSize.md,
        value=field_type._get_default_value(),  # fixme:检查tortoise-orm的获取默认值
    )
    res.update(kwargs)
    return res


def get_columns_from_model(
    model: Type[Model],
    include: Tuple[str, ...] = (),
    exclude: Tuple[str, ...] = (),
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    todo：增加多对多字段显示
    """
    fields = model._meta.fields_map

    res = []
    for field, field_type in fields.items():
        if include and field not in include or exclude and field in exclude:
            logger.error("can not found field:", field)
            continue
        if isinstance(field_type, (IntEnumFieldInstance, CharEnumFieldInstance)):
            res.append(
                Mapping(
                    name=field,
                    label=field,
                    map={k: v for k, v in field_type.enum_type.choices.items()},
                )
            )
            # fixme:处理开关字段
        # elif isinstance(field_type,):#fixme:处理特殊字段，比如json字段，或者图片、开关等需要特殊显示的类型。
        elif isinstance(field_type, ManyToManyFieldInstance):
            continue
        else:
            res.append(Column(name=field, label=field))
    return res


def get_controls_from_model(
    model: Type[Model],
    include: Tuple[str, ...] = (),
    exclude: Tuple[str, ...] = (),
    extra_fields: Optional[Tuple[Column, ...]] = None,
    exclude_readonly: bool = False,
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    extra_fields:额外的自定义字段
    """
    fields = model._meta.fields_map
    res = []
    for field, field_type in fields.items():
        if include and field not in include or (exclude and field in exclude):
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
                        min=field_type.constraints.get("ge") or None,
                        max=field_type.constraints.get("le") or None,
                        precision=0,
                        step=1,
                        **_get_base_attr(field_type),
                        validations={
                            "minimum": field_type.constraints.get("ge") or None,
                            "maximum": field_type.constraints.get("le") or None,
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
                            "maxLength": field_type.max_length or None,
                        },
                    )
                )
        # todo:等待完成,另，需要完成date
        elif isinstance(field_type, DatetimeField):
            res.append(
                DatetimeItem(
                    **_get_base_attr(field_type),
                    format="YYYY-MM-DD HH:mm:ss",
                    inputFormat="YYYY-MM-DD HH:mm:ss",
                )
            )
        elif isinstance(field_type, DateField):
            res.append(
                DateItem(
                    **_get_base_attr(field_type),
                    format="YYYY-MM-DD",
                    inputFormat="YYYY-MM-DD",
                )
            )
        elif isinstance(field_type, TimeDeltaField):
            res.append(
                TimeItem(
                    **_get_base_attr(field_type),
                    format="HH:mm",
                    inputFormat="HH:mm",
                    timeConstrainst=False,
                )
            )
        elif isinstance(field_type, CharEnumFieldInstance):  # fixme:需要修复
            print(field_type.enum_type)
        elif isinstance(field_type, BooleanField):
            if field_type.default is False:
                res.append(
                    SwitchItem(
                        type="switch",
                        name=field_type.model_field_name,
                        label="开关",
                        trueValue=True,
                        falseValue=False,
                        value=True,  # fixme：测试是否具有默认值
                    )
                )
            else:
                enum_type = {"True": True, "False": False}
                res.append(
                    SelectItem(
                        options=[
                            SelectOption(label=label, value=value) for value, label in enum_type
                        ],
                        **_get_base_attr(
                            field_type,
                            default={"label": "True", "value": True}
                            if field_type.default
                            else {"label": "False", "value": False},
                        ),
                    ),
                )
        elif isinstance(field_type, FloatField):
            validation = {}
            if field_type.constraints.get("ge") and field_type.constraints.get("le"):
                validation["minimum"] = field_type.constraints.get("ge")
                validation["maximum"] = field_type.constraints.get("le")
            res.append(
                NumberItem(
                    min=field_type.constraints.get("ge"),
                    max=field_type.constraints.get("le"),
                    precision=None,
                    step=1,
                    showSteps=None,
                    **_get_base_attr(field_type),
                    validations=validation,
                )
            )
        elif isinstance(field_type, DecimalField):
            validation = {}
            validation["minimum"] = field_type.constraints.get("ge")
            validation["maximum"] = field_type.constraints.get("le")
            res.append(
                NumberItem(
                    min=field_type.constraints.get("ge"),
                    max=field_type.constraints.get("le"),
                    precision=2,
                    step=1,
                    showSteps=None,
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
            res.append(UUIDItem(**_get_base_attr(field_type), length=None))
        elif isinstance(field_type, ManyToManyFieldInstance):  # 多对多字段
            if field_type.generated:
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
            if field_type.generated:
                res.append(
                    SelectItem(
                        **_get_base_attr(field_type, required=False),
                        source=f"get:/{field_type.model_field_name}-selects",
                    )
                )
        elif isinstance(field_type, ForeignKeyFieldInstance):
            if field_type.generated:
                res.append(
                    SelectItem(
                        **_get_base_attr(field_type, required=False),
                        source=f"get:/{field_type.model_field_name}-selects",
                    )
                )
        else:
            raise ValueError(f"{field}字段的字段类型尚不支持!")
    if extra_fields:
        res.extend(extra_fields)
    return res
def make_columns(
    model: Type[Model],
    include: Tuple[str, ...] = (),
    exclude: Tuple[str, ...] = (),
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    todo：增加多对多字段显示
    """
    fields = model._meta.fields_map

    res = []
    for field, field_type in fields.items():
        if include and field not in include or exclude and field in exclude:
            continue
        if isinstance(field_type, (IntEnumFieldInstance, CharEnumFieldInstance)):
            res.append(
                Mapping(
                    name=field,
                    label=field,
                    map={k: v for k, v in field_type.enum_type.choices.items()},
                )
            )
            # fixme:处理开关字段
        # elif isinstance(field_type,):#fixme:处理特殊字段，比如json字段，或者图片、开关等需要特殊显示的类型。
        elif isinstance(field_type, ManyToManyFieldInstance):
            continue
        else:
            res.append(Column(name=field, label=field))
    return res
