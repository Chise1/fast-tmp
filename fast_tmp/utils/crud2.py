import inspect
from typing import Callable, List, Optional, Tuple, Type

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel
from starlette import status
from tortoise import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.query_utils import Q

from fast_tmp.depends.auth import get_user_has_perms
from fast_tmp.utils.pydantic_creator import pydantic_offsetlimit_creator


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
                    filter_, kind=inspect.Parameter.KEYWORD_ONLY, annotation=str, default="__null__"
                )
            )
    # noinspection Mypy,PyArgumentList
    func.__signature__ = inspect.Signature(parameters=res, __validate_parameters__=False)


def create_pydantic_schema(
    model: Type[Model],
    name: str,
    fields: Optional[Tuple[str, ...]] = None,
    exclude_readonly: bool = False,
) -> Type[BaseModel]:
    if fields:
        return pydantic_model_creator(
            model, name=name, include=fields, exclude_readonly=exclude_readonly
        )
    else:
        return pydantic_model_creator(model, name=name, exclude_readonly=exclude_readonly)


def create_list_route(
    route: APIRouter,
    path: str,
    model: Type[Model],
    fields: Optional[Tuple[str, ...]] = None,
    codenames: Optional[Tuple[str, ...]] = None,
    searchs: Optional[Tuple[str, ...]] = None,
    filters: Optional[Tuple[str, ...]] = None,
    res_pydantic_model: Optional[Type[BaseModel]] = None,
    random_str: str = "",
):
    """
    创建list的路由
    """
    if res_pydantic_model:
        schema = res_pydantic_model
    else:
        schema = create_pydantic_schema(
            model, f"CREATORList{model.__name__}{path.replace('/', '_')}{random_str}", fields=fields
        )
    if searchs:

        async def model_list(
            search: Optional[str] = None,
            **kwargs,
        ):
            query = model.all()
            if search:
                x = [Q(**{f"{i}__contains": search}) for i in searchs]
                if x:
                    q = x[0]
                    for i in x[1:]:
                        q = q | i
                    query = query.filter(q)
            if kwargs:
                s = {}
                for k, v in kwargs.items():
                    if not v == "__null__":
                        s[k] = v
                    else:
                        pass
                if s:
                    query = query.filter(**s)
            data = await query
            return [schema.from_orm(i) for i in data]

    else:

        async def model_list(
            **kwargs,
        ):
            query = model.all()
            if kwargs:
                s = {}
                for k, v in kwargs.items():
                    if not v == "__null__":
                        s[k] = v
                    else:
                        pass
                if s:
                    query = query.filter(**s)
            data = await query
            return [schema.from_orm(i) for i in data]

    add_filter(model_list, filters)
    route.get(
        path, dependencies=[Depends(get_user_has_perms(codenames))], response_model=List[schema]
    )(model_list)


def create_list_route_with_page(
    route: APIRouter,
    path: str,
    model: Type[Model],
    fields: Optional[Tuple[str, ...]] = None,
    codenames: Optional[Tuple[str, ...]] = None,
    searchs: Optional[Tuple[str, ...]] = None,
    filters: Optional[Tuple[str, ...]] = None,
    res_pydantic_model: Optional[Type[BaseModel]] = None,
    random_str: str = "",
):
    """
    创建list的路由
    """
    if res_pydantic_model:
        schema = res_pydantic_model
    else:
        schema = create_pydantic_schema(
            model,
            f"CREATORList{model.__name__}{path.replace('/', '_')}Page{random_str}",
            fields=fields,
        )
    paging_schema = pydantic_offsetlimit_creator(schema)
    if searchs:

        async def model_list(
            offset: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
            **kwargs,
        ):
            count = model.all()
            query = model.all().limit(limit).offset(offset)
            if search:
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
                    if not v == "__null__":
                        s[k] = v
                    else:
                        pass
                if s:
                    query = query.filter(**s)
                    count = count.filter(**s)

            data = await query
            return paging_schema(total=await count.count(), data=[schema.from_orm(i) for i in data])

    else:

        async def model_list(
            offset: int = 0,
            limit: int = 10,
            **kwargs,
        ):
            count = model.all()
            query = model.all().limit(limit).offset(offset)
            if kwargs:
                s = {}
                for k, v in kwargs.items():
                    if not v == "__null__":
                        s[k] = v
                    else:
                        pass
                if s:
                    query = query.filter(**s)
                    count = count.filter(**s)

            data = await query
            return paging_schema(total=await count.count(), data=[schema.from_orm(i) for i in data])

    add_filter(model_list, filters)
    route.get(
        path, dependencies=[Depends(get_user_has_perms(codenames))], response_model=paging_schema
    )(model_list)


def create_retrieve_route(
    route: APIRouter,
    path: str,
    model: Type[Model],
    fields: Optional[Tuple[str, ...]] = None,
    codenames: Optional[Tuple[str, ...]] = None,
    res_pydantic_model: Optional[Type[BaseModel]] = None,
    random_str: str = "",
):
    if res_pydantic_model:
        schema = res_pydantic_model
    else:
        schema = create_pydantic_schema(
            model,
            f"CREATORRetrieve{model.__name__}{path.replace('/', '_')}ID{random_str}",
            fields=fields,
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
    random_str: str = "",
):
    if res_pydantic_model:
        schema = res_pydantic_model
    else:
        schema = create_pydantic_schema(
            model,
            name=f"CREATORPost{model.__name__}{path.replace('/', '_')}{random_str}",
            fields=fields,
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
    random_str: str = "",
):
    if res_pydantic_model:
        schema = res_pydantic_model
    else:
        schema = create_pydantic_schema(
            model,
            f"CREATORPut{model.__name__}{path.replace('/', '_')}{random_str}",
            fields=fields,
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
