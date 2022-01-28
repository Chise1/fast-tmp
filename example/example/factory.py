from fast_tmp.conf import settings  # 放第一个不要变
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title='{{cookiecutter.project_slug}}', debug=settings.DEBUG)
    # 注册app的位置
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in
                           settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    # app.middleware("http")(cas_middleware)
    # 在cookie存储session
    # app.add_middleware(SessionMiddleware, secret_key=settings.CAS_SESSION_SECRET)
    return app
