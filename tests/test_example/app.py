import os

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "test_example.settings")

from fastapi import Depends
from test_example.admin import AuthorModel, BookModel, FieldTestingModel
from tortoise.contrib.fastapi import register_tortoise

from fast_tmp.conf import settings
from fast_tmp.depends.auth import get_current_active_user
from fast_tmp.factory import create_app
from fast_tmp.models import Group, Permission, User
from fast_tmp.site import register_model_site

register_model_site({"fieldtesting": [FieldTestingModel(), BookModel(), AuthorModel()]})
app = create_app()
app.title = "test_example"


@app.get("/perms")
async def get_perms(
    codename: str,
    user: User = Depends(get_current_active_user),
):
    """
    测试权限
    """
    codenames = codename.split(",")
    permissions = await Permission.filter(codename__in=codenames)
    group = Group()
    group.name = "za"
    group.permissions.add(*permissions)
    await group.save()
    return await user.has_perm(codename)


register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=True)
if settings.DEBUG:
    from starlette.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory="static"), name="static")  # 注册admin页面需要的静态文件，

if __name__ == "__main__":
    import uvicorn  # type:ignore

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
