from typing import List, Union

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from starlette.requests import Request
from tortoise import Model
from tortoise.transactions import in_transaction

from .creator import AbstractApp
from .depends import get_model
from .schema.page import Page

router = APIRouter()


class ListDataWithPage(BaseModel):  # 带分页的数据
    items: List[dict]
    total: int = 0


class BaseRes(BaseModel):
    status: int = 0
    msg: str = ""
    data: Union[dict, BaseModel] = {}


def get_abstract_app():
    return AbstractApp._instance


def get_app_page(resource: str, app: AbstractApp = Depends(get_abstract_app)):
    return app.get_page(resource).schema


@router.get("/{resource}/list", response_model=BaseRes)
async def list_view(
    request: Request,
    page: Page = Depends(get_app_page),
    model: Model = Depends(get_model),
    page_size: int = 10,
    page_num: int = 1,
):
    qs = model.all()
    params = request.query_params
    qs = qs.filter(**params)
    total = await qs.count()
    qs = qs.limit(page_size).offset((page_num - 1) * page_size)
    values = await qs.values(*page._list_fields)
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
    page: Page = Depends(get_app_page),
    model: Model = Depends(get_model),
):
    update_fields = page._update_fields
    data = await model.filter(pk=pk).first().values(
        *update_fields)  # fixme:是字典还是列表？
    return BaseRes(data=data)


@router.post("/{resource}/create")
async def create(
    request: Request,
    page: Page = Depends(get_app_page),
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
async def bulk_delete(request: Request, ids: DIDS,
                      model: Model = Depends(get_model)):
    await model.filter(pk__in=ids.ids).delete()
    return BaseRes()
