from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

# from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from fast_tmp.conf import settings  # 放第一个不要变
from fast_tmp.depends.auth import register_app

settings._init_model()


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
    app = FastAPI(title="test_example", debug=settings.DEBUG)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    # 注册app的位置
    register_app(app)
    from test_example.apps.api.v1 import router

    from fast_tmp.admin.server import admin

    app.include_router(router)
    app.mount("/admin", admin)
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    if settings.SENTRY_DSN:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIROMENT,
        )
        # Sentry的插件
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

        app.add_middleware(SentryAsgiMiddleware)
    # app.middleware("http")(cas_middleware)
    # 在cookie存储session
    # app.add_middleware(SessionMiddleware, secret_key=settings.CAS_SESSION_SECRET)
    register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=True)
    init_app(app)
    return app
