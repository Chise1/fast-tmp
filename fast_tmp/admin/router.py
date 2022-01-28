from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from starlette.requests import Request

from fast_tmp.conf import settings
from ..model_site import get_model_site, ModelAdmin, model_list

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


@router.get("/{resource}/list")
async def list_view(
        request: Request,
        abstract_crud: AbstractCRUD = Depends(get_app_page),
        model_site: Optional[ModelAdmin] = Depends(get_model_site),
        perPage: int = 10,
        page: int = 1,
):
    if not model_site:
        return BaseRes()
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
        model_site: Optional[ModelAdmin] = Depends(get_model_site),
        pk: int = Path(...),
):
    data = await request.json()
    obj = await model.filter(pk=pk).using_db(conn).select_for_update().get()
    await obj.update_from_dict(data).save(using_db=conn)
    return BaseRes()


@router.get("/{resource}/update/{pk}")
async def update_view(
        request: Request,
        pk: int = Path(...),
        page: AbstractCRUD = Depends(get_app_page),
        model_site: Optional[ModelAdmin] = Depends(get_model_site),
):
    update_fields = page.up_include
    data = await model.filter(pk=pk).first().values(*update_fields)  # fixme:是字典还是列表？
    return BaseRes(data=data)


@router.post("/{resource}/create")
async def create(
        request: Request,
        page: AbstractCRUD = Depends(get_app_page),
        model_site: Optional[ModelAdmin] = Depends(get_model_site),
):
    data = await request.json()
    await model.create(**data)
    return BaseRes(data=data)


@router.delete("/{resource}/delete/{pk}")
async def delete(request: Request, pk: int, model=Depends(get_model)):
    await model.filter(pk=pk).delete()
    return BaseRes()


class DIDS(BaseModel):
    ids: List[int]


@router.post("/{resource}/deleteMany/")
async def bulk_delete(request: Request, ids: DIDS,
                      model_site: Optional[ModelAdmin] = Depends(get_model_site),

                      ):
    await model.filter(pk__in=ids.ids).delete()
    return BaseRes()


@router.get("/{resource}/schema")
async def get_schema(
        request: Request,
        resource: str,
        page: AbstractCRUD = Depends(get_app_page),
        model_site: Optional[ModelAdmin] = Depends(get_model_site),
):
    return page.get_Page().dict(exclude_none=True)


@router.get("/site")
async def get_data():
    pages=[]
    for name,model in model_list.items():
        pages.append(
            {"label":name,
             "api":"/admin/"+name+"/schema"}
        )
    return BaseRes(data={"pages": {
        "pages":pages
    }})
