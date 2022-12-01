from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fast_tmp.admin.server import admin
from fast_tmp.conf import settings


def create_app() -> FastAPI:
    """
    初始化app,并连接tortoise-orm
    :return: FastAPI
    """
    app = FastAPI(debug=settings.DEBUG)
    # 注册app的位置
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    # 在cookie存储session
    # app.add_middleware(SessionMiddleware, secret_key=settings.CAS_SESSION_SECRET)

    app.mount("/admin", admin, name="admin")

    return app
