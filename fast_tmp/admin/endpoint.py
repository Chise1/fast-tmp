from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from fastapi.params import Path
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import RedirectResponse

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
    datas = await page_model.list(request, perPage, page - 1)
    return BaseRes(
        data=ListDataWithPage(
            total=datas["total"],
            items=datas["items"],
        )
    )


@router.get("/{resource}/select/{field_name}")
async def list_view(
    request: Request,
    field_name: str,
    perPage: Optional[int] = None,
    page: Optional[int] = None,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    datas = await page_model.select_options(field_name, request, perPage, page)
    return BaseRes(data=datas)


@router.post("/{resource}/patch/{pk}")
async def patch_data(
    request: Request,
    pk: str,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    data = await request.json()
    await page_model.patch(request, pk, data)
    return BaseRes().dict()


#
#
# @router.put("/{resource}/update")
# def update_data(
#     request: Request,
#     page_model: ModelAdmin = Depends(get_model_site),
#     session: Session = Depends(get_db_session),
#     data: dict = Depends(get_data),
#     user: Optional[User] = Depends(decode_access_token_from_data),
# ):
#     if not user:
#         return RedirectResponse(request.url_for("admin:login"))
#     data = clean_data_to_model(page_model.get_clean_fields(page_model.update_fields), data)
#     w = search_pk_list(page_model.model, request)
#     if isinstance(w, BaseRes):
#         return w
#     old_data = session.execute(select(page_model.model).where(*w)).scalar_one_or_none()
#     if not old_data:
#         return not_found_instance
#     page_model.update_model(old_data, data, session)
#     session.commit()
#     return BaseRes()
#
#
# @router.get("/{resource}/update")
# def update_view(
#     request: Request,
#     page_model: ModelAdmin = Depends(get_model_site),
#     session: Session = Depends(get_db_session),
#     user: Optional[User] = Depends(decode_access_token_from_data),
# ):
#     if not user:
#         return RedirectResponse(request.url_for("admin:login"))
#
#     pks = search_pk_list(page_model.model, request)
#     if isinstance(pks, BaseRes):
#         return pks
#     data = session.execute(select(page_model.model).where(*pks)).scalar_one_or_none()
#     if not data:
#         return not_found_instance
#     res = {}
#     for i in page_model.update_fields:
#         if isinstance(i.property, RelationshipProperty):
#             prop = i.property
#             if prop.direction in (MANYTOMANY,):  # TODO need onetomany
#                 pk = list(get_pk(prop.entity.class_).keys())[0]  # 只支持单主键
#                 res[i.key] = [getattr(sub, pk) for sub in getattr(data, i.key)]  # type: ignore
#         else:
#             res[i.key] = getattr(data, i.key)  # type: ignore
#
#     return BaseRes(data=res)
#
#
@router.post("/{resource}/create")
async def create(
    request: Request,
    page_model: ModelAdmin = Depends(get_model_site),
    user: Optional[User] = Depends(__get_user),
):
    data = await request.json()
    await page_model.create(request, data)
    return BaseRes(data=data)


#
#
# @router.delete("/{resource}/delete")
# def delete_one(
#     request: Request,
#     page_model: ModelAdmin = Depends(get_model_site),
#     session: Session = Depends(get_db_session),
#     user: Optional[User] = Depends(decode_access_token_from_data),
# ):
#     if not user:
#         return RedirectResponse(request.url_for("admin:login"))
#
#     w = search_pk_list(page_model.model, request)
#     if isinstance(w, BaseRes):
#         return w
#     session.execute(delete(page_model.model).where(*w))
#     session.commit()
#     return BaseRes()


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


# @router.get("/{resource}/selects/{field}")
# def get_selects(
#     request: Request,
#     field: str = Path(...),  # type: ignore
#     page_model: ModelAdmin = Depends(get_model_site),
#     user: Optional[User] = Depends(decode_access_token_from_data),
#     session: Session = Depends(get_db_session),
#     perPage: int = 10,
#     page: int = 1,
# ):
#     items = []
#     total = 0
#     for attr in page_model.mapper().attrs:
#         if attr.key == field:
#             relation_model = attr.entity.class_
#             secondary = attr.secondary
#             for col in secondary.foreign_key_constraints:
#                 if col.referred_table in page_model.mapper().tables:
#                     params = dict(request.query_params)
#                     if len(params) > 1:
#                         raise single_pk
#                     col_name = col.column_keys[0]
#                     for c in secondary.c:
#                         if c.key == col_name:
#                             clean_value = clean_param(c.type, list(params.values())[0])
#                             sql = (
#                                 select(*list(get_pk(relation_model).values()))
#                                 .join(secondary)
#                                 .where(c == clean_value)
#                                 .limit(perPage)
#                                 .offset((page - 1) * perPage)
#                             )
#                             datas = session.execute(sql)
#                             total_f = session.execute(
#                                 select(func.count())
#                                 .select_from(relation_model)
#                                 .join(secondary)
#                                 .where(col == list(params.values())[0])
#                             ).fetchone()
#                             if total_f is not None:
#                                 total = total_f[0]
#                             for data in datas:
#                                 items.append(dict(data))
#     return BaseRes(data={"total": total, "rows": items})
#
#
# @router.get("/{resource}/picks/{field}")
# def get_picks(
#     request: Request,
#     field: str = Path(...),  # type: ignore
#     page_model: ModelAdmin = Depends(get_model_site),
#     user: Optional[User] = Depends(decode_access_token_from_data),
#     session: Session = Depends(get_db_session),
#     perPage: int = 10,
#     page: int = 1,
# ):
#     """
#     枚举选择
#     """
#     source_field = getattr(page_model.model, field)
#     if isinstance(source_field.property, RelationshipProperty):
#         relation_model = source_field.property.mapper.class_
#
#     else:
#         relation_model = source_field.property.mapper.class_
#     datas = session.execute(
#         select(list(get_pk(relation_model).values())).limit(perPage).offset((page - 1) * perPage)
#     )
#     items = []
#     for data in datas:
#         items.append(dict(data))
#     s = session.execute(select(func.count()).select_from(relation_model))
#     total = 0
#     for i in s:
#         total = i[0]
#     return BaseRes(data={"total": total, "rows": items})
