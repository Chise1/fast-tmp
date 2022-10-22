import os

from starlette.requests import Request

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "test_example.settings")

from test_example.admin import AuthorModel, BookModel, FieldTestingModel
from test_example.page import UserSelfInfo
from tortoise.contrib.fastapi import register_tortoise

from fast_tmp.admin.register import register_static_service
from fast_tmp.conf import settings
from fast_tmp.factory import create_app
from fast_tmp.models import User
from fast_tmp.responses import BaseRes
from fast_tmp.site import register_model_site

register_model_site(
    {"fieldtesting": [FieldTestingModel(), BookModel(), AuthorModel(), UserSelfInfo()]}
)
app = create_app()
app.title = "test_example"


@app.get("/ss")
async def create_user():
    user = User(username="admin")
    user.set_password("123456")
    user.name = "admin"
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    await user.save()


@app.post("/form-test")
async def test_form(request: Request):
    print(await request.json())
    return BaseRes()


register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=True)
if settings.DEBUG:
    register_static_service(app)

if __name__ == "__main__":
    import uvicorn  # type:ignore

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
