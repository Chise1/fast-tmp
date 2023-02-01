from fastapi import FastAPI

from fast_tmp.admin.server import admin
from fast_tmp.conf import settings


def create_app() -> FastAPI:
    """
    初始化app,并连接tortoise-orm
    :return: FastAPI
    """
    app = FastAPI(debug=settings.DEBUG)
    app.mount("/admin", admin, name="admin")

    return app
