from typing import Optional

from fastapi import APIRouter, Depends
from starlette.requests import Request

from fast_tmp.admin.depends import get_staff
from fast_tmp.responses import BaseRes
from fast_tmp.site import ModelSession, RegisterRouter, get_model_site

router = APIRouter()


@router.get("/{resource}/list", dependencies=[Depends(get_staff)])
async def list_view(
    request: Request,
    page_model: ModelSession = Depends(get_model_site),
    perPage: int = 10,
    page: int = 1,
):
    datas = await page_model.list(request, perPage, page)
    return BaseRes(data=datas)


@router.get("/{resource}/prefetch/{field_name}", dependencies=[Depends(get_staff)])
async def prefetch_view(
    request: Request,
    field_name: str,
    pk: Optional[str] = None,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelSession = Depends(get_model_site),
):
    """
    对多对多外键进行额外的加载
    """
    datas = await page_model.select_options(request, field_name, pk, perPage, page)
    return BaseRes(data=datas)


@router.get("/{resource}/select/{field_name}", dependencies=[Depends(get_staff)])
async def select_view(
    request: Request,
    field_name: str,
    pk: Optional[str] = None,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelSession = Depends(get_model_site),
):
    """
    枚举字段的额外加载，主要用于外键
    """
    datas = await page_model.select_options(request, field_name, pk, perPage, page)
    return BaseRes(data=datas)


@router.post("/{resource}/patch/{pk}", dependencies=[Depends(get_staff)])
async def patch_data(
    request: Request,
    pk: str,
    page_model: ModelSession = Depends(get_model_site),
):
    """
    内联模式快速修改需要的接口
    """
    data = await request.json()
    await page_model.patch(request, pk, data)
    return BaseRes().dict()


@router.put("/{resource}/update/{pk}", dependencies=[Depends(get_staff)])
async def update_data(
    request: Request,
    pk: str,
    page_model: ModelSession = Depends(get_model_site),
):
    data = await request.json()
    await page_model.update(request, pk, data)


@router.get("/{resource}/update/{pk}", dependencies=[Depends(get_staff)])
async def update_view(
    request: Request,
    pk: str,
    page_model: ModelSession = Depends(get_model_site),
):
    data = await page_model.get_update(request, pk)
    return BaseRes(data=data)


@router.post("/{resource}/create", dependencies=[Depends(get_staff)])
async def create(
    request: Request,
    page_model: ModelSession = Depends(get_model_site),
):
    data = await request.json()
    await page_model.create(request, data)


@router.delete("/{resource}/delete/{pk}", dependencies=[Depends(get_staff)])
async def delete_func(
    request: Request,
    pk: str,
    page_model: ModelSession = Depends(get_model_site),
):
    await page_model.delete(request, pk)
    return BaseRes()


@router.get("/{resource}/schema", dependencies=[Depends(get_staff)])
async def get_schema(
    request: Request,
    page: RegisterRouter = Depends(get_model_site),
):
    return BaseRes(data=await page.get_app_page(request))
