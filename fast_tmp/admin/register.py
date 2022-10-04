from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from fast_tmp.conf import settings


def register_static_server(app: FastAPI):
    """
    加载静态文件的服务
    """
    app.mount(
        "/" + settings.STATIC_ROOT, StaticFiles(directory=settings.STATIC_PATH), name="static"
    )  # 注册admin页面需要的静态文件，
    app.mount(
        "/" + settings.MEDIA_ROOT, StaticFiles(directory=settings.MEDIA_PATH), name="media"
    )  # 注册admin页面需要的静态文件，
