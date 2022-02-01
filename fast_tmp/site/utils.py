import warnings
from typing import Dict, List, Tuple

from sqlalchemy import BigInteger, Column, Enum, Integer, SmallInteger, inspect
from sqlalchemy.orm import Mapper

from fast_tmp.admin.schema.forms import Column as FormColumn
from fast_tmp.admin.schema.forms import FormWidgetSize, ItemModel
from fast_tmp.admin.schema.forms.widgets import NumberItem, TextItem


def get_pk(model) -> Dict[str, Column]:
    mapper: Mapper = inspect(model)
    primary_keys: Tuple[Column, ...] = mapper.primary_key
    return {pk.name: pk for pk in primary_keys}


def _get_base_attr(field_type: Column, **kwargs) -> dict:
    res = dict(
        className=None,
        inputClassName=None,
        labelClassName=None,
        name=field_type.name,
        label=field_type.name,
        labelRemark=None,
        description=None,
        placeholder=None,
        inline=False,
        submitOnChange=False,
        disabled=False,
        disableOn=None,
        required=not field_type.nullable,
        mode=ItemModel.normal,
        size=FormWidgetSize.full,
        value=field_type.default() if callable(field_type.default) else field_type.default,
    )
    res.update(kwargs)
    return res


def get_controls_from_model(
    include: Tuple[Column, ...] = (),
) -> List[FormColumn]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    extra_fields:额外的自定义字段
    """
    res = []
    for field in include:
        if isinstance(field.type, Enum):
            pass
        elif isinstance(field.type, BigInteger):
            pass
        elif isinstance(field.type, SmallInteger):
            pass
        elif isinstance(field.type, Integer):
            res.append(
                NumberItem(
                    min=field.type.constraints.get("ge") or -2147483648,
                    max=field.type.constraints.get("le") or 2147483647,
                    precision=0,
                    step=1,
                    **_get_base_attr(field.type),
                    validations={
                        "minimum": field.type.constraints.get("ge") or -2147483648,
                        "maximum": field.type.constraints.get("le") or 2147483647,
                    },
                ),
            )
        else:
            item = TextItem(
                **_get_base_attr(field),
            )
            if getattr(field.type, "length"):
                validations = {
                    "maxLength": field.type.length,
                }
                item.validations = validations
            res.append(item)
            warnings.warn("Not found form type")
    return res


def get_columns_from_model(
    include: Tuple[Column, ...] = (),
) -> List[Column]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    todo：增加多对多字段显示
    """
    res = []
    for field in include:
        # if isinstance(field_type, (IntEnumFieldInstance, CharEnumFieldInstance)):
        #     res.append(
        #         Mapping(
        #             name=field,
        #             label=field,
        #             map={k: v for k, v in field_type.enum_type.choices.items()},
        #         )
        #     )
        #     fixme:处理开关字段
        # elif isinstance(field_type,):#fixme:处理特殊字段，比如json字段，或者图片、开关等需要特殊显示的类型。
        # elif isinstance(field_type, ManyToManyFieldInstance):
        #     continue
        # else:
        res.append(FormColumn(name=field.name, label=field.name))
    return res
