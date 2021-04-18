import inspect
from typing import Callable, Optional, Tuple, Type

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel
from starlette import status
from tortoise import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.query_utils import Q

from fast_tmp.depends.auth import get_user_has_perms


class Empty_:
    pass


def add_filter(func: Callable, filters: Optional[Tuple[str, ...]] = None):
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
    # noinspection Mypy
    func.__signature__ = inspect.Signature(parameters=res, __validate_parameters__=False)


def create_list_route(
    route: APIRouter,
    path: str,
    model: Type[Model],
    fields: Optional[Tuple[str, ...]] = None,
    codenames: Optional[Tuple[str, ...]] = None,
    searchs: Optional[Tuple[str, ...]] = None,
    filters: Optional[Tuple[str, ...]] = None,
    res_pydantic_model: Optional[Type[BaseModel]] = None,
):
    """
    创建list的路由
    """
    if res_pydantic_model:
        schema = res_pydantic_model
    elif fields:
        schema = pydantic_model_creator(
            model,
            name=f"CREATORList{model.__name__}{path.replace('/', '_')}",
            include=fields,
        )
    else:
        schema = pydantic_model_creator(
            model, name=f"CREATORList{model.__name__}{path.replace('/', '_')}"
        )

    async def model_list(
        offset: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        **kwargs,
    ):
        count = model.all()
        query = model.all().limit(limit).offset(offset)
        if search and searchs:
            x = [Q(**{f"{i}__contains": search}) for i in searchs]
            if x:
                q = x[0]
                for i in x[1:]:
                    q = q | i
                query = query.filter(q)
                count = count.filter(q)
        if kwargs:
            s = {}
            for k, v in kwargs.items():
                if not v == Empty_:
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


def create_retrieve_route(
    route: APIRouter,
    path: str,
    model: Type[Model],
    fields: Optional[Tuple[str, ...]] = None,
    codenames: Optional[Tuple[str, ...]] = None,
    res_pydantic_model: Optional[Type[BaseModel]] = None,
):
    if res_pydantic_model:
        schema = res_pydantic_model
    elif fields:
        schema = pydantic_model_creator(
            model,
            name=f"CREATORRetrieve{model.__name__}{path.replace('/', '_')}ID",
            include=fields,
        )
    else:
        schema = pydantic_model_creator(
            model, name=f"CREATORRetrieve{model.__name__}{path.replace('/', '_')}ID"
        )

    async def model_retrieve(
        id: int,
    ):
        instance = await model.get(pk=id)
        return schema.from_orm(instance).dict()

    route.get(path + "/{id}", dependencies=[Depends(get_user_has_perms(codenames))])(model_retrieve)


def create_delete_route(
    route: APIRouter,
    path: str,
    model: Type[Model],
    codenames: Optional[Tuple[str, ...]] = None,
):
    """
    删除路由生成器
    """

    async def model_delete(
        id: int,
    ):
        await model.filter(pk=id).delete()

    route.delete(
        path + "/{id}",
        dependencies=[Depends(get_user_has_perms(codenames))],
        status_code=status.HTTP_200_OK,
    )(model_delete)


# fixme:等待测试
def create_post_route(
    route: APIRouter,
    path: str,
    model: Type[Model],
    fields: Optional[Tuple[str, ...]] = None,
    codenames: Optional[Tuple[str, ...]] = None,
    res_pydantic_model: Optional[Type[BaseModel]] = None,
):
    if res_pydantic_model:
        schema = res_pydantic_model
    elif fields:
        schema = pydantic_model_creator(
            model, name=f"CREATORPost{model.__name__}{path.replace('/', '_')}In", include=fields
        )
    else:
        schema = pydantic_model_creator(
            model,
            name=f"CREATORPost{model.__name__}{path.replace('/', '_')}In",
            exclude_readonly=True,
        )

    async def model_post(
        info: schema,
    ):
        await model.create(**info.dict())

    route.post(path, dependencies=[Depends(get_user_has_perms(codenames))])(model_post)


# fixme:等待测试
def create_put_route(
    route: APIRouter,
    path: str,
    model: Type[Model],
    fields: Optional[Tuple[str, ...]] = None,
    codenames: Optional[Tuple[str, ...]] = None,
    res_pydantic_model: Optional[Type[BaseModel]] = None,
):
    if res_pydantic_model:
        schema = res_pydantic_model
    elif fields:
        schema = pydantic_model_creator(
            model, name=f"CREATORPut{model.__name__}{path.replace('/', '_')}In", include=fields
        )
    else:
        schema = pydantic_model_creator(
            model,
            name=f"CREATORPut{model.__name__}{path.replace('/', '_')}In",
            exclude_readonly=True,
        )

    async def model_put(
        id: int,
        info: schema,
    ):
        await model.filter(pk=id).update(**info.dict())

    route.put(
        path + "/{id}",
        dependencies=[Depends(get_user_has_perms(codenames))],
    )(model_put)
