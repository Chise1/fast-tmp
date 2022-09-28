import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Type

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from fast_tmp.amis.page import Page
from fast_tmp.amis.view.card import Card, CardHeader
from fast_tmp.amis.view.divider import Divider
from fast_tmp.responses import BaseRes, NoAuthError
from fast_tmp.site.base import RegisterRouter

logger = logging.getLogger(__file__)


def get_user(request: Request):
    user = request.user
    if not user:
        raise NoAuthError()


class userinfoData(BaseModel):
    name: str
    avator: str


class IndexPage(RegisterRouter):

    def get_userinfo(self):
        @self._router.get("/userinfo")
        async def userinfo(request: Request, ):
            user = request.user
            if not user:
                raise NoAuthError()
            return BaseRes(data={
                "name": user.name,
                "avator": user.avatar or user.name[0:1],
            })

        @self._router.put("/userinfo")
        async def mod_userinfo(request: Request, userinfo: userinfoData):
            user = request.user
            user.name = userinfo.name
            user.avatar = userinfo.avator
            await user.save()

    def __init__(self, prefix: str, name: str, app: Optional[FastAPI] = None):
        router = APIRouter()
        super().__init__(prefix, name, app, router)
        self._router.dependencies = [get_user]

    async def get_app_page(self, request: Request) -> Page:  # todo增加修改个人信息的页面
        user = request.user
        return Page(
            body=[Card(
                header=CardHeader(
                    title=user.name,
                    subTitle=user.name + "的副标题",  # todo 需要增加信息？
                    description=user.name + "的描述",
                    avatar=user.avatar or user.name[0:1],
                ),
                body=[Divider()],
            )]
        )
