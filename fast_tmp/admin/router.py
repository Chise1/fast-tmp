from typing import Any, List

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from starlette.requests import Request
from tortoise import Model
from tortoise.transactions import in_transaction

from fast_tmp.conf import settings

from ..utils.common import import_module
from .creator import AbstractApp, AbstractCRUD
from .depends import get_model

router = APIRouter()


class ListDataWithPage(BaseModel):  # 带分页的数据
    items: List[dict]
    total: int = 0


class BaseRes(BaseModel):
    status: int = 0
    msg: str = ""
    data: Any = {}


def get_abstract_app():
    return AbstractApp._instance


def get_app_page(resource: str, app: AbstractApp = Depends(get_abstract_app)) -> AbstractCRUD:
    return app.get_AbstractCRUD(resource)


@router.get("/{resource}/list", response_model=BaseRes)
async def list_view(
    request: Request,
    abstract_crud: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
    perPage: int = 10,
    page: int = 1,
):
    qs = model.all()
    params = dict(request.query_params)
    params.pop("page")
    params.pop("perPage")
    if params:
        qs = qs.filter(**params)
    total = await qs.count()
    qs = qs.limit(perPage).offset((page - 1) * perPage)
    values = await qs.values(*abstract_crud.list_include)
    return BaseRes(
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
):
    data = await request.json()
    async with in_transaction() as conn:
        obj = await model.filter(pk=pk).using_db(conn).select_for_update().get()
        await obj.update_from_dict(data).save(using_db=conn)
    return BaseRes()


@router.get("/{resource}/update/{pk}")
async def update_view(
    request: Request,
    pk: int = Path(...),
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
):
    update_fields = page.up_include
    data = await model.filter(pk=pk).first().values(*update_fields)  # fixme:是字典还是列表？
    return BaseRes(data=data)


@router.post("/{resource}/create")
async def create(
    request: Request,
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
):
    data = await request.json()
    await model.create(**data)
    return BaseRes(data=data)


@router.delete("/{resource}/delete/{pk}")
async def delete(request: Request, pk: int, model: Model = Depends(get_model)):
    await model.filter(pk=pk).delete()
    return BaseRes()


class DIDS(BaseModel):
    ids: List[int]


@router.post("/{resource}/deleteMany/")
async def bulk_delete(request: Request, ids: DIDS, model: Model = Depends(get_model)):
    await model.filter(pk__in=ids.ids).delete()
    return BaseRes()


@router.get("/{resource}/schema")
async def get_schema(
    request: Request,
    resource: str,
    page: AbstractCRUD = Depends(get_app_page),
    model: Model = Depends(get_model),
):
    return page.get_Page().dict(exclude_none=True)


@router.get("/site")
async def get_data():
    module = import_module(settings.EXTRA_SETTINGS["ADMIN_SITE_CLASS"])
    return BaseRes(data={"pages": module.dict()})
