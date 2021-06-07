from typing import List, Set, Type

from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel
from starlette.requests import Request
from tortoise import (
    BackwardFKRelation,
    BackwardOneToOneRelation,
    ForeignKeyFieldInstance,
    ManyToManyFieldInstance,
    Model,
    OneToOneFieldInstance,
)
from tortoise.queryset import QuerySet
from tortoise.transactions import in_transaction

from fast_tmp.conf import settings

from ..models import User
from ..utils.common import import_module
from .auth import get_user_has_perms
from .creator import AbstractApp, AbstractCRUD
from .depends import get_model
from .res_model import AmisRes

router = APIRouter()


class ListDataWithPage(BaseModel):  # 带分页的数据
    items: List[dict]
    total: int = 0


def get_abstract_app():
    return AbstractApp._instance


def get_app_page(resource: str, app: AbstractApp = Depends(get_abstract_app)) -> AbstractCRUD:
    return app.get_AbstractCRUD(resource)


def get_fields(include_fields, exclude_fields, model):
    """
    获取要读取的字段
    """
    if not include_fields:
        map_keys = list(model._meta.fields_map.keys())
        fields = set(map_keys)
        for exclude_field in exclude_fields:
            try:
                fields.remove(exclude_field)
            except ValueError:
                pass
    else:
        fields = set(include_fields)
    relation_fields = set()  # 把多对多和反向外键关系去掉
    for field, field_type in model._meta.fields_map.items():
        if isinstance(field_type, (ManyToManyFieldInstance, BackwardFKRelation)):
            relation_fields.add(field)
    return fields - relation_fields


def get_model_amis_relation_label(model: Type[Model]):
    if hasattr(model, "Amis") and hasattr(model.Amis, "relation_label"):
        return model.Amis.relation_label
    return {}


def exclude_reference(fields: Set, model, load_relation_fields: bool = True):
    """
    清理关系字段（即生成的authoer_id等实际字段）
    检查并替换跨表查询字段
    :key load_relation_fields: 是否把外键返回为amis对应的字段，而不是id
    """
    relation_fields_rename = {}
    fields_value = set()
    for field in fields:
        if model._meta.fields_map[field].reference is not None:
            pass
        # elif load_relation_fields and get_model_amis_relation_label(model).get(field):
        #     relation_fields_rename[field] = field + "__" + model.Amis.relation_label.get(field)
        else:
            if model._meta.fields_map[field].source_field is not None:
                relation_fields_rename[field] = model._meta.fields_map[field].source_field
            else:
                fields_value.add(field)

    return fields_value, relation_fields_rename


def get_select_prefetch_fields(
    qs: QuerySet,
    fields,
    model,
):
    """
    确定需要额外加载那几张表
    """
    map_keys = list(model._meta.fields_map.keys())
    select_fields = []
    prefetch_fields = []
    for field in fields:
        if field not in map_keys:
            f = field.split("__")
            if len(f) != 2:
                raise ValueError(f"{model.__name__} don't have proetry: {field}")
            f_name, sub_name = f
            for k, field_type in model._meta.fields_map:
                if k == f_name:
                    if isinstance(
                        field_type,
                        (
                            ForeignKeyFieldInstance,
                            OneToOneFieldInstance,
                        ),
                    ):
                        select_fields.append(f_name)
                    elif isinstance(
                        field_type,
                        BackwardOneToOneRelation,
                    ):
                        prefetch_fields.append(f_name)
                    else:
                        pass
                    break
            else:
                raise ValueError(f"{model.__name__} don't have proetry: {field}")

    if select_fields:
        qs = qs.select_related(*select_fields)
    if prefetch_fields:
        qs = qs.prefetch_related(*prefetch_fields)
    return qs


@router.get("/{resource}/list", response_model=AmisRes)
async def list_view(
    request: Request,
    abstract_crud: AbstractCRUD = Depends(get_app_page),
    model: Type[Model] = Depends(get_model),
    perPage: int = 10,
    page: int = 1,
    user: User = Depends(get_user_has_perms()),
):
    qs = model.all()
    params = dict(request.query_params)
    params.pop("page")
    params.pop("perPage")
    if params:
        qs = qs.filter(**params)
    total = await qs.count()
    qs = qs.limit(perPage).offset((page - 1) * perPage)
    fields = get_fields(abstract_crud.list_include, abstract_crud.list_exclude, model)
    qs = get_select_prefetch_fields(qs, fields, model)
    fields, relation_fields_rename = exclude_reference(fields, model)
    values = await qs.values(*fields, **relation_fields_rename)
    return AmisRes(
        data=ListDataWithPage(
            total=total,
            items=values,
        ),
    )


@router.put("/{resource}/update/{pk}")
async def update(
    request: Request,
    model: Model = Depends(get_model),
    abstract_crud: AbstractCRUD = Depends(get_app_page),
    pk: int = Path(...),
    user: User = Depends(get_user_has_perms()),
):
    data: dict = await request.json()
    fields = get_fields(abstract_crud.up_include, abstract_crud.up_exclude, model)
    fields, relation_fields_rename = exclude_reference(fields, model)
    write_data = {}
    relation_fields_keys = relation_fields_rename.keys()
    for k, v in data.items():
        if k in fields:
            write_data[k] = v
        elif k in relation_fields_keys:
            write_data[relation_fields_rename[k]] = v
        else:
            pass
    async with in_transaction() as conn:
        obj = await model.filter(pk=pk).using_db(conn).select_for_update().get()
        await obj.update_from_dict(write_data).save(using_db=conn)
    return AmisRes()


@router.get("/{resource}/update/{pk}")
async def update_view(
    request: Request,
    pk: int = Path(...),
    abstract_crud: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    qs = model.filter(pk=pk)
    fields = get_fields(abstract_crud.up_include, abstract_crud.up_exclude, model)
    qs = get_select_prefetch_fields(qs, fields, model)
    fields, relation_fields_rename = exclude_reference(fields, model, load_relation_fields=False)
    data = await qs.values(*fields, **relation_fields_rename)  # fixme:是字典还是列表？
    return AmisRes(data=data)


@router.post("/{resource}/create")
async def create(
    request: Request,
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    data = await request.json()
    await model.create(**data)
    return AmisRes(data=data)


@router.delete("/{resource}/delete/{pk}")
async def delete(
    request: Request,
    pk: int,
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    await model.filter(pk=pk).delete()
    return AmisRes()


class DIDS(BaseModel):
    ids: List[int]


@router.post("/{resource}/deleteMany/")
async def bulk_delete(request: Request, ids: DIDS, model: Model = Depends(get_model)):
    await model.filter(pk__in=ids.ids).delete()
    return AmisRes()


@router.get("/{resource}/schema")
async def get_schema(
    request: Request,
    resource: str,
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    return page.get_Page().dict(exclude_none=True)


@router.get("/{resource}/select")
async def get_schema(
    request: Request,
    field: str = Query(
        ...,
    ),
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    field_model = model._meta.fields_map[field].related_model
    amis_c = getattr(model, "Amis", None)
    if (
        amis_c is not None
        and hasattr(amis_c, "relation_label")
        and amis_c.relation_label.get(field)
    ):
        return await field_model.all().values(value="id", label=amis_c.relation_label.get(field))
    else:
        return await field_model.all().values(label="id", value="id")


@router.get("/{resource}/mapping")
async def get_schema(
    request: Request,
    field: str = Query(
        ...,
    ),
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    field_model = model._meta.fields_map[field].related_model
    amis_c = getattr(model, "Amis", None)
    if (
        amis_c is not None
        and hasattr(amis_c, "relation_label")
        and amis_c.relation_label.get(field)
    ):
        data = await field_model.all().values(value="id", label=amis_c.relation_label.get(field))
    else:
        data = await field_model.all().values(label="id", value="id")
    res = {}
    for i in data:
        res[i["value"]] = i["label"]
    return AmisRes(data=res)


@router.get("/{resource}/backrelation/{pk}")
async def get_backrealtion_values(
    request: Request,
    field: str = Query(...),
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    field_model = model._meta.fields_map[field].related_model
    amis_c = getattr(model, "Amis", None)
    if (
        amis_c is not None
        and hasattr(amis_c, "relation_label")
        and amis_c.relation_label.get(field)
    ):
        return await field_model.all().values(
            field_model._meta.pk_attr, amis_c.relation_label.get(field)
        )
    else:
        return await field_model.all().values(field_model._meta.pk_attr)


@router.get("/site")
async def get_data(user: User = Depends(get_user_has_perms())):
    # fixme:修改为基于权限的返回
    module = import_module(settings.EXTRA_SETTINGS["ADMIN_SITE_CLASS"])
    return AmisRes(data={"pages": module.dict()})
