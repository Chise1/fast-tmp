from datetime import datetime
from typing import Dict, List, Optional, Text, Tuple

from sqlalchemy import (
    BOOLEAN,
    DECIMAL,
    INTEGER,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    Numeric,
    SmallInteger,
    inspect,
)
from sqlalchemy.orm import Mapper

from fast_tmp.admin.schema.forms import Column as AmisColumn
from fast_tmp.admin.schema.forms import Column as FormColumn
from fast_tmp.admin.schema.forms import Control, FormWidgetSize, ItemModel
from fast_tmp.admin.schema.forms.widgets import (
    DatetimeItem,
    NativeNumber,
    NumberItem,
    SwitchItem,
    TextareaItem,
    TextItem,
)


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
    )
    if field_type.default is not None:

        if callable(field_type.default):
            res["value"] = field_type.default()
        else:
            res["value"] = field_type.default.arg
    res.update(kwargs)
    return res


def get_controls_from_model(include: Tuple[Column, ...] = ()) -> List[Control]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    extra_fields:额外的自定义字段
    """
    res: List[Control] = []
    for field in include:
        item: Optional[Control] = None
        if isinstance(field.type, Enum):
            pass
        elif isinstance(field.type, (Boolean, BOOLEAN)):  # boolean's default value must be false.
            item = SwitchItem(
                **_get_base_attr(field),
            )
        elif isinstance(field.type, Float):
            item = NumberItem(
                **_get_base_attr(field),
            )
        elif isinstance(field.type, (DECIMAL, Numeric)):
            item = NativeNumber(
                **_get_base_attr(field),
            )
            # todo need add limit check
        # elif isinstance(field.type,Time):
        #     item = TimeItem(
        #         **_get_base_attr(field),
        #
        #     )
        elif isinstance(field.type, DateTime):
            item = DatetimeItem(  # fixme need check
                **_get_base_attr(field), format="YYYY-MM-DDTHH:mm:ss"
            )
        # elif isinstance(field.type, BigInteger):
        #     pass
        # elif isinstance(field.type, SmallInteger):
        #     pass
        elif isinstance(field.type, (Integer, INTEGER, BigInteger, SmallInteger)):
            # min = (
            #     field.type.constraints.get("ge")  # type :ignore
            #     if hasattr(field.type, "constraints")  # type :ignore
            #     else -2147483648  # type :ignore
            # )  # type :ignore
            # max = (  # type :ignore
            #     field.type.constraints.get("le")  # type :ignore
            #     if hasattr(field.type, "constraints")  # type :ignore
            #     else 2147483647  # type :ignore
            # )  # type :ignore
            item = NumberItem(
                # min=min,
                # max=max,
                precision=0,
                step=1,
                **_get_base_attr(field),
                # validations={
                #     "minimum": min,
                #     "maximum": max,
                # },
            )
        elif isinstance(field.type, Text):
            item = TextareaItem(
                **_get_base_attr(field),
            )
        else:
            item = TextItem(
                **_get_base_attr(field),
            )
            if hasattr(field.type, "length"):
                validations = {
                    "maxLength": field.type.length,
                }
                item.validations = validations
        if item is not None:
            res.append(item)
    return res


def get_columns_from_model(
    include: Tuple[Column, ...] = (),
) -> List[AmisColumn]:
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


def clean_data_to_model(model_field: Tuple[Column, ...], data: dict) -> dict:
    """
    把前端的数据转为后端的格式
    """
    for k in data:
        for i in model_field:
            if i.name == k:
                if isinstance(i.type, DateTime):
                    data[k] = datetime.strptime(data[k], "%Y-%m-%dT%H:%M:%S")
                break
        else:
            del data[k]
    return data
