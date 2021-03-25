from fastapi import FastAPI
from tmp.conf import settings
from .routes.hello_fast_tmp import hello_fast_tmp_router
example_app_app = FastAPI(
    title="example_app",
    debug=settings.DEBUG,
)
example_app_app.include_router(hello_fast_tmp_router)