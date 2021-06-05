from typing import List, Type

from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel
from starlette.requests import Request
from tortoise import BackwardOneToOneRelation, ForeignKeyFieldInstance, Model, OneToOneFieldInstance
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
    map_keys = list(model._meta.fields_map.keys())
    select_fields = []
    prefetch_fields = []
    if not abstract_crud.list_include:
        fields = map_keys
        for exclude_field in abstract_crud.list_exclude:
            try:
                fields.remove(exclude_field)
            except ValueError:
                pass
    else:
        fields = abstract_crud.list_include
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

    values = await qs.values(*fields)
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
    pk: int = Path(...),
    user: User = Depends(get_user_has_perms()),
):
    data = await request.json()
    async with in_transaction() as conn:
        obj = await model.filter(pk=pk).using_db(conn).select_for_update().get()
        await obj.update_from_dict(data).save(using_db=conn)
    return AmisRes()


@router.get("/{resource}/update/{pk}")
async def update_view(
    request: Request,
    pk: int = Path(...),
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    user: User = Depends(get_user_has_perms()),
):
    update_fields = page.up_include
    data = await model.filter(pk=pk).first().values(*update_fields)  # fixme:是字典还是列表？
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
    if amis_c is not None and hasattr(amis_c, "fk_label") and amis_c.fk_label.get(field):
        return await field_model.all().values(value="id", label=amis_c.fk_label.get(field))
    else:
        return await field_model.all().values(label="id", value="id")


@router.get("/site")
async def get_data(user: User = Depends(get_user_has_perms())):
    # fixme:修改为基于权限的返回
    module = import_module(settings.EXTRA_SETTINGS["ADMIN_SITE_CLASS"])
    return AmisRes(data={"pages": module.dict()})
