import inspect
from typing import Callable, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status
from tortoise import Model
from tortoise.query_utils import Q

from fast_tmp.depends.auth import get_user_has_perms


class Empty_:
    pass


def add_filter(func: Callable, filters: List[str] = None):
    signature = inspect.signature(func)
    res = []
    for k, v in signature.parameters.items():
        if k == "kwargs":
            continue
        res.append(v)
    if filters:
        for filter_ in filters:
            res.append(
                inspect.Parameter(
                    filter_, kind=inspect.Parameter.KEYWORD_ONLY, annotation=str, default=Empty_
                )
            )
    func.__signature__ = inspect.Signature(parameters=res, __validate_parameters__=False)


# fixme:等待测试
def create_list_route2(
    route: APIRouter,
    path: str,
    model: Model,
    schema: BaseModel,
    codenames: Optional[List[str]] = None,
    filters: Optional[List[str]] = None,
    searchs: Optional[List[str]] = None,
):
    """
    创建list的路由
    """

    async def model_list(
        offset: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        **kwargs,
    ):
        count = model.all()
        query = model.all().limit(limit).offset(offset)
        search_query = None
        filter_query = None
        if search and searchs:  # fixme:等待测试
            x = [Q(**{f"{i}__like": search}) for i in searchs]
            if x:
                q = x[0]
                for i in x[1:]:
                    q = q | i
                query = query.filter(q)
                count = count.filter(q)
        if kwargs:
            s = {}
            for k, v in kwargs.items():
                if v and not isinstance(v, Empty_):
                    s[k] = v
                else:
                    pass
            if s:
                query = query.filter(**s)
                count = count.filter(**s)
        data = await query
        return {"total": await count.count(), "items": [schema.from_orm(i) for i in data]}

    add_filter(model_list, filters)
    route.get(path, dependencies=[Depends(get_user_has_perms(codenames))])(model_list)


def create_list_route(
    route: APIRouter,
    path: str,
    model: Model,
    schema: BaseModel,
    codenames: Optional[List[str]] = None,
    searchs: Optional[List[str]] = None,
):
    """
    创建list的路由
    """

    async def model_list(
        offset: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ):
        count = model.all()
        query = model.all().limit(limit).offset(offset)
        if search and searchs:  # fixme:等待测试
            x = [Q(**{f"{i}__contains": search}) for i in searchs]
            if x:
                q = x[0]
                for i in x[1:]:
                    q = q | i
                query = query.filter(q)
                count = count.filter(q)
        total = count.count()
        data = await query
        return {"total": await total, "items": [schema.from_orm(i) for i in data]}

    route.get(path, dependencies=[Depends(get_user_has_perms(codenames))])(model_list)


def create_retrieve_route(
    route: APIRouter,
    path: str,
    model: Model,
    schema: BaseModel,
    codenames: Optional[List[str]] = None,
):
    async def model_retrieve(
        id: int,
    ):
        instance = await model.get(pk=id)
        return schema.from_orm(instance).dict()

    route.get(path + "/${id}", dependencies=[Depends(get_user_has_perms(codenames))])(
        model_retrieve
    )


# fixme:等待测试
def create_delete_route(
    route: APIRouter,
    path: str,
    model: Model,
    codenames: Optional[List[str]] = None,
):
    """
    删除路由生成器
    """

    async def model_delete(
        id: int,
    ):
        await model.filter(pk=id).delete()

    route.delete(
        path + "/${id}",
        dependencies=[Depends(get_user_has_perms(codenames))],
        status_code=status.HTTP_200_OK,
    )(model_delete)


# fixme:等待测试
def create_post_route(
    route: APIRouter,
    path: str,
    model: Model,
    schema: BaseModel,  # 不要有id
    codenames: Optional[List[str]] = None,
):
    async def model_post(
        info: schema,
    ):
        instance = await model.create(**info.dict())
        return schema.from_orm(instance)

    route.post(path, dependencies=[Depends(get_user_has_perms(codenames))])(model_post)


# fixme:等待测试
def create_put_route(
    route: APIRouter,
    path: str,
    model: Model,
    schema: BaseModel,  # 不要有id
    codenames: Optional[List[str]] = None,
):
    async def model_put(
        id: int,
        info: schema,
    ):
        await model.filter(pk=id).update(**info.dict())

    route.put(path + "/${id}", dependencies=[Depends(get_user_has_perms(codenames))])(model_put)


#
# def create_enum_route(
#         route: APIRouter,
#         model: Model,
#         path: str = "/enum-selects",
#         label_name: str = None,
#         codenames: Optional[List[str]] = None,
# ):
#     """
#     针对字段专门创建枚举路由
#     """
#
#     def column_get(
#             column: str,
#             session: Session = Depends(get_db_session),
#     ):
#         if column[-3:] == "_id":
#             select_model = getattr(model, column[0:-3]).comparator.mapper.class_
#         else:
#             select_model = getattr(model, column).comparator.mapper.class_
#
#         if label_name:
#             results = session.execute(
#                 select(select_model.id, getattr(select_model, label_name))
#             ).all()
#             return [{"value": result[0], "label": result[1]} for result in
#                     results]
#         else:
#             results = session.execute(
#                 select(select_model.id)).all()  # fixme；先不考虑返回字段的枚举值
#             return [{"value": result, "label": result} for result in results]
#
#     route.get(path, codenames=codenames)(column_get)
