from starlette.applications import Starlette
# from starlette.middleware.sessions import SessionMiddleware
from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings
from starlette.middleware.cors import CORSMiddleware
from fast_tmp import factory
# from fast_tmp.depends.cas import cas_middleware
# from fast_tmp.redis import AsyncRedisUtil
from {{cookiecutter.project_slug}}.apps.api import {{cookiecutter.project_slug}}_app

def init_app(main_app: Starlette):
    @main_app.on_event("startup")
    async def startup() -> None:
        pass
        # await AsyncRedisUtil.init(**settings.REDIS)

    @main_app.on_event("shutdown")
    async def shutdown() -> None:
        pass
        # await AsyncRedisUtil.close()


def create_app() -> AmisAPI:
    app = AmisAPI(title='fast_tmp example', debug=settings.DEBUG)
    settings.app = app

    r_app = factory.create_fast_tmp_app()
    app.mount(settings.FAST_TMP_URL, r_app)
    app.mount("/api",{{cookiecutter.project_slug}}_app)
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
    # 在cookie存儲session
    # app.add_middleware(SessionMiddleware, secret_key=settings.CAS_SESSION_SECRET)
    init_app(app)
    return app
