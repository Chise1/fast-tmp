from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.requests import Request

from fast_tmp.depends.auth import get_current_active_user
from fast_tmp.site import ModelAdmin, get_model_site

from ..models import User
from ..responses import BaseRes, ListDataWithPage
from .depends import __get_user

router = APIRouter()


async def get_data(request: Request) -> dict:
    """
    从异步函数里面读取数据
    """
    return await request.json()


@router.get("/{resource}/list")
async def list_view(
    request: Request,
    page_model: ModelAdmin = Depends(get_model_site),
    perPage: int = 10,
    page: int = 1,
    user: Optional[User] = Depends(__get_user),
):
    datas = await page_model.list(request, perPage, page)
    return BaseRes(
        data=ListDataWithPage(
            total=datas["total"],
            items=datas["items"],
        )
    )


@router.get("/{resource}/prefetch/{field_name}")
async def prefetch_view(
    request: Request,
    field_name: str,
    pk: Optional[str] = None,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    """
    对多对多外键进行额外的加载
    """
    datas = await page_model.select_options(request, field_name, pk, perPage, page)
    return BaseRes(data=datas)


@router.get("/{resource}/select/{field_name}")
async def select_view(
    request: Request,
    field_name: str,
    pk: Optional[str] = None,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    """
    枚举字段的额外加载，主要用于外键
    """
    datas = await page_model.select_options(request, field_name, pk, perPage, page)
    return BaseRes(data=datas)


@router.post("/{resource}/patch/{pk}")
async def patch_data(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    """
    内联模式快速修改需要的接口
    """
    data = await request.json()
    await page_model.patch(request, pk, data)
    return BaseRes().dict()


@router.put("/{resource}/update/{pk}")
async def update_data(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    data = await request.json()
    data = await page_model.put(request, pk, data)
    return BaseRes(data=data)


@router.get("/{resource}/update/{pk}")
async def update_view(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    data = await page_model.put_get(request, pk)
    return BaseRes(data=data)


@router.post("/{resource}/create")
async def create(
    request: Request,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    data = await request.json()
    await page_model.create(request, data)
    return BaseRes(data=data)


@router.delete("/{resource}/delete/{pk}")
async def delete_func(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    await page_model.delete(request, pk)
    return BaseRes()


# def clean_param(field_type, param: str):
#     if isinstance(
#         field_type, (Integer, DECIMAL, BigInteger, Float, INTEGER, Numeric, SmallInteger)
#     ):
#         return int(param)
#     elif isinstance(field_type, DateTime):
#         return datetime.strptime(param, "%Y-%m-%dT%H:%M:%S")
#     else:
#         return param
#

#
# def search_pk_list(model, request: Request):
#     """
#     获取要查询的单个instance的主键
#     """
#     params = dict(request.query_params)
#     pks = get_pk(model)
#     w = []
#     for k, v in params.items():
#         if pks.get(k) is not None:
#             field = pks[k]
#             if isinstance(
#                 field.type, (Integer, DECIMAL, BigInteger, Float, INTEGER, Numeric, SmallInteger)
#             ):
#                 w.append(pks[k] == int(v))
#             elif isinstance(field.type, DateTime):
#                 w.append(pks[k] == datetime.strptime(v, "%Y-%m-%dT%H:%M:%S"))
#             else:
#                 w.append(pks[k] == v)
#         else:
#             return key_error
#     return w


class DIDS(BaseModel):
    ids: List[int]


#  todo next version
# @router.post("/{resource}/deleteMany/")
# def bulk_delete(request: Request, ids: DIDS,
#                 model_site: Optional[ModelAdmin] = Depends(get_model_site),
#
#                 ):
#     # await model.filter(pk__in=ids.ids).delete()
#     return BaseRes()


@router.get("/{resource}/schema")
async def get_schema(
    request: Request,
    page: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    return BaseRes(data=await page.get_app_page(request))
