
import os

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "example.settings")

from fast_tmp.models import User, Group
from tortoise.contrib.fastapi import register_tortoise
from fast_tmp.conf import settings
from fast_tmp.factory import create_app

app = create_app()
app.title = "test_example"

register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=True)
if settings.DEBUG:
    from starlette.staticfiles import StaticFiles
    path = os.path.dirname(__file__)
    app.mount("/static", StaticFiles(directory=os.path.join(path, "static")), name="static")  # 注册admin页面需要的静态文件，


# @app.on_event("startup")
# async def tt() -> None:  # pylint: disable=W0612
#     user = await User.filter(username="admin").first()
#     group1 = Group(name="group1")
#     group2 = Group(name="group2")
#     await Group.bulk_create([group1, group2])
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
