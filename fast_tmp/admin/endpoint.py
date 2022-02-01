from typing import Any, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import Session
from starlette.requests import Request

from fast_tmp.site import get_model_site, ModelAdmin

from .creator import AbstractApp, AbstractCRUD
from ..db import get_db_session
from ..site.utils import get_pk

router = APIRouter()


async def get_data(request: Request) -> dict:
    """
    从异步函数里面读取数据
    """
    return await request.json()


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
def list_view(
        page_model: ModelAdmin = Depends(get_model_site),
        perPage: int = 10,
        page: int = 1,
        session: Session = Depends(get_db_session)
):
    datas = session.execute(select(page_model.list_display).limit(perPage).offset((page - 1) * perPage))
    items = []
    for data in datas:
        items.append(dict(data))
    s = session.execute(select(func.count()).select_from(page_model.model))
    total = 0
    for i in s:
        total = i[0]
    return BaseRes(
        data=ListDataWithPage(
            total=total,
            items=items,
        )
    )


@router.put("/{resource}/update")
def update_data(
        request: Request,
        page_model: ModelAdmin = Depends(get_model_site),
        session: Session = Depends(get_db_session),
        data: dict = Depends(get_data)
):
    params = dict(request.query_params)
    pks = get_pk(page_model.model)
    w = []
    for k, v in params.items():
        if pks.get(k) is not None:
            w.append(pks[k] == v)
    session.execute(update(page_model.model).where(*w).values(**data))  # todo need check field is truely
    session.commit()
    return BaseRes()


@router.get("/{resource}/update")
def update_view(
        request: Request,
        page_model: ModelAdmin = Depends(get_model_site),
        session: Session = Depends(get_db_session),
):
    params = dict(request.query_params)
    pks = get_pk(page_model.model)
    w = []
    for k, v in params.items():
        if pks.get(k) is not None:
            w.append(pks[k] == v)
    data = session.execute(select(page_model.update_fields).where(*w))
    for i in data:
        return BaseRes(data=dict(i))


@router.post("/{resource}/create")
def create(
        data: dict = Depends(get_data),
        page_model: ModelAdmin = Depends(get_model_site),
        session: Session = Depends(get_db_session),
):
    model = page_model.model
    instance = model(**data)
    session.add(instance)
    session.commit()
    return BaseRes(data=data)


@router.delete("/{resource}/delete")
def delete_one(
        request: Request,
        page_model: ModelAdmin = Depends(get_model_site),
        session: Session = Depends(get_db_session),
):
    params = dict(request.query_params)
    pks = get_pk(page_model.model)
    w = []
    for k, v in params.items():
        if pks.get(k) is not None:
            w.append(pks[k] == v)
        else:
            return BaseRes(status=400, msg="主键错误")
    session.execute(delete(page_model.model).where(*w))
    session.commit()
    return BaseRes()


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
def get_schema(
        page: ModelAdmin = Depends(get_model_site),
):
    return BaseRes(
        data=page.get_app_page()
    )
