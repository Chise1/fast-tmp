import os

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "test_example.settings")
from fast_tmp.factory import create_app
from fast_tmp.conf import settings
from tortoise.contrib.fastapi import register_tortoise
from fast_tmp.site import register_model_site
from test_example.admin import FieldTestingModel

register_model_site({"fieldtesting": [FieldTestingModel()]})
app = create_app()
app.title = "test_example"

register_tortoise(app, config=settings.TORTOISE_ORM,generate_schemas=True)
if settings.DEBUG:
    from starlette.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory="static"), name="static")  # 注册admin页面需要的静态文件，

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
