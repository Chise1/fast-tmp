from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.requests import Request

from fast_tmp.site import ModelAdmin, get_model_site

from ..models import User
from ..responses import BaseRes, ListDataWithPage
from .depends import get_user

router = APIRouter()


@router.get("/{resource}/list", dependencies=[Depends(get_user)])
async def list_view(
    request: Request,
    page_model: ModelAdmin = Depends(get_model_site),
    perPage: int = 10,
    page: int = 1,
):
    datas = await page_model.list(request, perPage, page)
    return BaseRes(
        data=ListDataWithPage(
            total=datas["total"],
            items=datas["items"],
        )
    )


@router.get("/{resource}/prefetch/{field_name}", dependencies=[Depends(get_user)])
async def prefetch_view(
    request: Request,
    field_name: str,
    pk: Optional[str] = None,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelAdmin = Depends(get_model_site),
):
    """
    对多对多外键进行额外的加载
    """
    datas = await page_model.select_options(request, field_name, pk, perPage, page)
    return BaseRes(data=datas)


@router.get("/{resource}/select/{field_name}", dependencies=[Depends(get_user)])
async def select_view(
    request: Request,
    field_name: str,
    pk: Optional[str] = None,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelAdmin = Depends(get_model_site),
):
    """
    枚举字段的额外加载，主要用于外键
    """
    datas = await page_model.select_options(request, field_name, pk, perPage, page)
    return BaseRes(data=datas)


@router.post("/{resource}/patch/{pk}", dependencies=[Depends(get_user)])
async def patch_data(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
):
    """
    内联模式快速修改需要的接口
    """
    data = await request.json()
    await page_model.patch(request, pk, data)
    return BaseRes().dict()


@router.put("/{resource}/update/{pk}", dependencies=[Depends(get_user)])
async def update_data(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
):
    data = await request.json()
    data = await page_model.put(request, pk, data)
    return BaseRes(data=data)


@router.get("/{resource}/update/{pk}", dependencies=[Depends(get_user)])
async def update_view(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
):
    data = await page_model.put_get(request, pk)
    return BaseRes(data=data)


@router.post("/{resource}/create", dependencies=[Depends(get_user)])
async def create(
    request: Request,
    page_model: ModelAdmin = Depends(get_model_site),
):
    data = await request.json()
    await page_model.create(request, data)
    return BaseRes(data=data)


@router.delete("/{resource}/delete/{pk}", dependencies=[Depends(get_user)])
async def delete_func(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
):
    await page_model.delete(request, pk)
    return BaseRes()


# class DIDS(BaseModel):
#     ids: List[int]


#  todo next version
# @router.post("/{resource}/deleteMany/")
# def bulk_delete(request: Request, ids: DIDS,
#                 model_site: Optional[ModelAdmin] = Depends(get_model_site),
#
#                 ):
#     # await model.filter(pk__in=ids.ids).delete()
#     return BaseRes()


@router.get("/{resource}/schema", dependencies=[Depends(get_user)])
async def get_schema(
    request: Request,
    page: ModelAdmin = Depends(get_model_site),
):
    return BaseRes(data=page.get_app_page(request))
