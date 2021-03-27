from fastapi import FastAPI
from fast_tmp.conf import settings
from .routes.hello_fast_tmp import hello_fast_tmp_router
{{cookiecutter.app_name}}_app = FastAPI(
    title="{{cookiecutter.app_name}}",
    debug=settings.DEBUG,
)
{{cookiecutter.app_name}}_app.include_router(hello_fast_tmp_router)