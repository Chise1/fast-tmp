from datetime import datetime
from typing import Dict, List, Optional, Text, Tuple, Union

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
from sqlalchemy.orm import MANYTOMANY, MANYTOONE, ONETOMANY, Mapper, RelationshipProperty

from fast_tmp.amis.actions import DialogAction
from fast_tmp.amis.forms import Column as AmisColumn
from fast_tmp.amis.forms import Column as FormColumn
from fast_tmp.amis.forms import Control, FormWidgetSize, ItemModel
from fast_tmp.amis.forms.widgets import (
    DatetimeItem,
    NativeNumber,
    NumberItem,
    PickerItem,
    SwitchItem,
    TextareaItem,
    TextItem,
)
from fast_tmp.amis.frame import Dialog
from fast_tmp.amis.zs import ZS, ZSTable


def get_pk(model) -> Dict[str, Column]:
    mapper: Mapper = inspect(model)
    primary_keys: Tuple[Column, ...] = mapper.primary_key
    return {pk.name: pk for pk in primary_keys}


def _get_base_attr(field_type: Column, **kwargs) -> dict:
    res = dict(
        className=None,
        inputClassName=None,
        labelClassName=None,
        name=field_type.key,
        label=field_type.key,
        labelRemark=None,
        description=None,
        placeholder=None,
        inline=False,
        submitOnChange=False,
        disabled=False,
        disableOn=None,
        required=not field_type.nullable if hasattr(field_type, "nullable") else False,
        mode=ItemModel.normal,
        size=FormWidgetSize.full,
    )
    if hasattr(field_type, "default") and field_type.default is not None:
        if callable(field_type.default):
            res["value"] = field_type.default()
        else:
            res["value"] = field_type.default.arg
    if isinstance(field_type.property, RelationshipProperty):
        col = field_type.property.local_remote_pairs[0][0]
        if not col.nullable:
            res["required"] = True
    res.update(kwargs)
    return res


def get_picker_item(field):
    property = field.property
    if property.direction == MANYTOONE:
        for_col = get_pk_column(field)
        real_col = get_real_column_field(field)
        item = PickerItem(
            name=real_col.key,
            label=field.key,
            required=not field.nullable if hasattr(field, "nullable") else False,
            valueField=for_col.key,
            labelField=for_col.key,
            source=f"endpoint/{field.parent.class_.__name__}/picks/{property.key}",
            pickerSchema={
                "mode": "table",
                "name": for_col.key,
                "columns": make_columns((for_col,)),  # todo 增加自定义显示列表
            },
        )
    elif property.direction == MANYTOMANY:
        real_column = get_real_column_field(field)
        item = PickerItem(
            **_get_base_attr(field),
            valueField=real_column.key,
            labelField=real_column.key,
            source=f"endpoint/{field.parent.class_.__name__}/picks/{property.key}?",
            pickerSchema={
                "mode": "table",
                "name": property.key,
                "columns": make_columns((real_column,)),  # todo 增加自定义显示列表
            },
            multiple=True,
        )
    elif property.direction == ONETOMANY:  # todo onetoone,onetomany
        item = None
        pass
    else:
        item = None
        ...  # todo need check
    return item


def make_controls(include: Tuple[Column, ...] = ()) -> List[Control]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    extra_fields:额外的自定义字段
    """
    res: List[Control] = []
    for field in include:
        item: Optional[Control] = None
        if isinstance(field.property, RelationshipProperty):
            item = get_picker_item(field)
        else:
            if isinstance(field.type, Enum):
                pass
            elif isinstance(
                field.type, (Boolean, BOOLEAN)
            ):  # boolean's default value must be false.
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


def make_columns(
    include: Tuple[Column, ...] = (),
) -> List[Union[AmisColumn, DialogAction]]:
    """
    从pydantic_queryset_creator创建的schema获取字段
    """
    res: List[Union[AmisColumn, DialogAction]] = []
    for field in include:
        if hasattr(field, "property"):
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


def clean_data_to_model(model_field: Tuple[Column, ...], data: dict) -> dict:
    """
    把前端的数据转为后端的格式
    """
    ret = {}
    for k in data:
        for i in model_field:
            if i.key == k:
                if isinstance(i.property, RelationshipProperty):  # 关系字段
                    if i.property.direction == MANYTOONE:
                        continue
                else:
                    if isinstance(i.type, DateTime):  # todo 关系和数据两种类型的要分开处理和判断
                        data[k] = datetime.strptime(data[k], "%Y-%m-%dT%H:%M:%S")
                ret[k] = data[k]
    return data


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


def get_pk_column(field):
    """
    获取多对一关系字段中对应表的主键字段
    """
    key = field.property.local_remote_pairs[0][1].key
    for f in field.parent.attrs:
        if f.key == key:
            return f.class_attribute
    else:
        raise Exception(f"Not found {key}")


def get_real_pk_column(field):
    """
    获取多对多关系对方表的主键字段
    """
    return get_pk(field.property.entity.class_)
