from typing import Optional, Tuple, Type

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel
from starlette import status
from tortoise import Model
from tortoise.query_utils import Q

from fast_tmp.depends.auth import get_user_has_perms
from fast_tmp.utils.crud_tools import add_filter
from fast_tmp.utils.pydantic import pydantic_model_creator
from fast_tmp.utils.pydantic_creator import pydantic_offsetlimit_creator


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


class Crud(BaseModel):
    list_fields: Tuple[str, ...]
    retrieve_fields: Tuple[str, ...]
    post_fields: Tuple[str, ...]
    put_fields: Tuple[str, ...]
    methods: Tuple[str, ...] = ("GET", "POST", "PUT", "DELETE", "RETRIEVE")
    router: APIRouter
    path: str
    codenames: Tuple[str, ...]
    list_schema: Optional[Type[BaseModel]] = None
    post_schema: Optional[Type[BaseModel]] = None
    put_schema: Optional[Type[BaseModel]] = None
    paging_schema: Optional[Type[BaseModel]] = None
    retrieve_schema: Optional[Type[BaseModel]] = None
    search_fields: Optional[Tuple[str, ...]] = None
    filter_fields: Optional[Tuple[str, ...]] = None
    model: Type[Model]

    def init(self):
        if self.__class__.__name__ == "Crud":
            raise TypeError("Could not init Crud,must inherit first!")

    def list(
        self,
    ):
        """
        创建list的路由
        """
        if not self.list_schema:
            self.list_schema = create_pydantic_schema(
                self.model,
                f"{self.__class__.__name__}L{self.model.__name__}{self.path.replace('/', '_')}P",
                fields=self.list_fields,
            )
        if not self.paging_schema:
            self.paging_schema = pydantic_offsetlimit_creator(self.list_schema)

        async def model_list(
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            search: Optional[str] = None,
            **kwargs,
        ):
            if offset and limit:
                query = self.model.all().limit(limit).offset(offset)
                count = self.model.all()
            else:
                query = self.model.all()
                count = None
            if search and self.search_fields:
                x = [Q(**{f"{i}__contains": search}) for i in self.search_fields]
                if x:
                    q = x[0]
                    for i in x[1:]:
                        q = q | i
                    query = query.filter(q)
                    if count is not None:
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
                    if count is not None:
                        count = count.filter(**s)

            data = await query
            if count:
                return self.paging_schema(
                    total=await count.count(), data=[self.list_schema.from_orm(i) for i in data]
                )
            else:
                return [self.list_schema.from_orm(i) for i in data]

        add_filter(model_list, self.filter_fields)
        self.router.get(
            self.path,
            dependencies=[Depends(get_user_has_perms(self.codenames))],
        )(model_list)

    def retrieve(
        self,
    ):
        if not self.retrieve_schema:
            self.retrieve_schema = create_pydantic_schema(
                self.model,
                f"{self.__class__.__name__}R{self.model.__name__}{self.path.replace('/', '_')}ID",
                fields=self.retrieve_fields,
            )

        async def model_retrieve(
            id: int,
        ):
            instance = await self.model.get(pk=id)
            return self.retrieve_schema.from_orm(instance).dict()

        self.router.get(
            self.path + "/{id}", dependencies=[Depends(get_user_has_perms(self.codenames))]
        )(model_retrieve)

    def delete(
        self,
    ):
        """
        删除路由生成器
        """

        async def model_delete(
            id: int,
        ):
            await self.model.filter(pk=id).delete()

        self.router.delete(
            self.path + "/{id}",
            dependencies=[Depends(get_user_has_perms(self.codenames))],
            status_code=status.HTTP_200_OK,
        )(model_delete)

    def post(
        self,
    ):
        if not self.post_schema:
            self.post_schema = create_pydantic_schema(
                self.model,
                name=f"{self.__class__.__name__}Po{self.model.__name__}{self.path.replace('/', '_')}",
                fields=self.post_fields,
                exclude_readonly=True,
            )
        post_schema = self.post_schema

        async def model_post(
            info: post_schema,
        ):
            await self.model.create(**info.dict())

        self.router.post(self.path, dependencies=[Depends(get_user_has_perms(self.codenames))])(
            model_post
        )

    def put(
        self,
    ):
        if not self.put_schema:
            self.put_schema = create_pydantic_schema(
                self.model,
                f"{self.__class__.__name__}Pu{self.model.__name__}{self.path.replace('/', '_')}",
                fields=self.put_schema,
                exclude_readonly=True,
            )
        put_schema = self.put_schema

        async def model_put(
            id: int,
            info: put_schema,
        ):
            await self.model.filter(pk=id).update(**info.dict())

        self.router.put(
            self.path + "/{id}",
            dependencies=[Depends(get_user_has_perms(self.codenames))],
        )(model_put)
