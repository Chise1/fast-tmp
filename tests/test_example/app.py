import os

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "test_example.settings")
from test_example.admin import AuthorModel, BookModel, FieldTestingModel
from tortoise.contrib.fastapi import register_tortoise

from fast_tmp.conf import settings
from fast_tmp.factory import create_app
from fast_tmp.site import register_model_site

register_model_site({"fieldtesting": [FieldTestingModel(), BookModel(), AuthorModel()]})
app = create_app()
app.title = "test_example"

# @app.get("/perms")
# async def get_perms(codename: str, user: Optional[User] = Depends(__get_user),
#                     ):
#     """
#     测试权限
#     """


register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=True)
if settings.DEBUG:
    from starlette.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory="static"), name="static")  # 注册admin页面需要的静态文件，

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
