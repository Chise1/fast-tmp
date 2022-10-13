import os

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from fast_tmp.conf import settings


def register_static_service(app: FastAPI):
    """
    加载静态文件的服务
    """
    if not os.path.exists(settings.STATIC_PATH):
        os.mkdir(settings.STATIC_PATH)
    app.mount(
        "/" + settings.STATIC_ROOT, StaticFiles(directory=settings.STATIC_PATH), name="static"
    )  # 注册admin页面需要的静态文件
    if not os.path.exists(settings.MEDIA_PATH):
        os.mkdir(settings.MEDIA_PATH)
    app.mount("/" + settings.MEDIA_ROOT, StaticFiles(directory=settings.MEDIA_PATH), name="media")
