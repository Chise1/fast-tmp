from fast_tmp.conf import settings #放第一个不要变
from starlette.applications import Starlette
# from starlette.middleware.sessions import SessionMiddleware
from tortoise.contrib.fastapi import register_tortoise
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def init_app(main_app: Starlette):
    @main_app.on_event("startup")
    async def startup() -> None:
        pass
        # await AsyncRedisUtil.init(**settings.REDIS)

    @main_app.on_event("shutdown")
    async def shutdown() -> None:
        pass
        # await AsyncRedisUtil.close()


def create_app() -> FastAPI:
    app = FastAPI(title='{{cookiecutter.project_slug}}', debug=settings.DEBUG)
    # 注册app的位置

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Sentry的插件
    # app.add_middleware(SentryAsgiMiddleware)
    # app.middleware("http")(cas_middleware)
    # 在cookie存储session
    # app.add_middleware(SessionMiddleware, secret_key=settings.CAS_SESSION_SECRET)
    register_tortoise(app, config=settings.TORTOISE_ORM)
    init_app(app)
    return app
