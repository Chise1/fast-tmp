from typing import List, Optional, Tuple, Type, Union, Dict
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
from tortoise.fields import Field
from tortoise import fields

from fast_tmp.amis.schema.actions import DialogAction
from fast_tmp.amis.schema.forms import Column, Mapping, ItemModel, FormWidgetSize
from fast_tmp.amis.schema.forms.widgets import (
    DateItem,
    DatetimeItem,
    NumberItem,
    SelectItem,
    SelectOption,
    SwitchItem,
    TextItem,
    TimeItem,
    UUIDItem, PickerItem,
)

logger = getLogger(__file__)


def get_pk(model: Model) -> Dict[str, Field]:
    return {"pk": model._meta.pk}


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
        size=FormWidgetSize.full,
        value=field_type._get_default_value(),  # fixme:检查tortoise-orm的获取默认值
    )
    res.update(kwargs)
    return res


def get_picker_item(field_type:Field):
    if isinstance(field_type,fields.ManyToManyField): # TODO 需要测试
        real_column = get_real_column_field(field_type)
        item = PickerItem(
            **_get_base_attr(field_type),
            valueField=real_column.key,
            labelField=real_column.key,
            source=f"{field_type.}/picks/{field_type.__name__}?", # todo 需要测试
            pickerSchema={
                "mode": "table",
                "name": property.key,
                "columns": make_columns((real_column,)),  # todo 增加自定义显示列表
            },
            multiple=True,
        )
    elif isinstance(field_type,fields.ForeignKeyField):  # todo onetoone,onetomany
        item = None
        pass
    elif isinstance(field_type,fields.OneToOneField):
        item = None
        pass
    else:
        item = None
        ...  # todo need check
    return item


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

def get_real_column_field(field):
    """
    获取多对一关系字段中自身的外键字段
    """
    key = field.property.local_remote_pairs[0][0].key
    for f in field.parent.attrs:
        if f.key == key:
            return f.class_attribute
    else:
        raise Exception(f"Not found {key}")

from fast_tmp.amis.schema.forms import Column as AmisColumn
from fast_tmp.amis.schema.forms import Column as FormColumn
def make_columns(
    include: Tuple[Field, ...] = (),
) -> List[Union[AmisColumn, DialogAction]]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    """
    res: List[Union[AmisColumn, DialogAction]] = []
    for field in include:
        if hasattr(field, "property"):
            if isinstance(field,ManyToManyFieldInstance):

            if isinstance(field.property, RelationshipProperty):  # 除了多对一显示主键，其他都显示加载按钮
                if field.property.direction == MANYTOONE:
                    real_col = get_real_column_field(field)
                    res.append(FormColumn(name=real_col.key, label=field.key))  # todo 考虑增加字符串识别方式
                elif field.property.direction == MANYTOMANY:
                    primary_keys = get_pk(field.class_).keys()
                    res.append(
                        DialogAction(
                            label=field.key,
                            dialog=Dialog(
                                title=field.key,
                                body=ZS(
                                    api=f"endpoint/{field.class_.__name__}/selects/{field.key}?"
                                    + "&".join([f"{pk}=${pk}" for pk in primary_keys]),
                                    body=ZSTable(
                                        title=field.key,
                                        name=field.key,
                                        source="$rows",
                                        columns=make_columns(
                                            tuple(get_real_pk_column(field).values())
                                        ),
                                    ),
                                ),
                            ),
                        )
                    )
                elif field.property.direction == ONETOMANY:  # todo need onetomany,onetoone
                    continue
                else:
                    continue  # todo need check

            else:
                res.append(FormColumn(name=field.key, label=field.key))
        else:
            res.append(FormColumn(name=field.key, label=field.key))
    return res