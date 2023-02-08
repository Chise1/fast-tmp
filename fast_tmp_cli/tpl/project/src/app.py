from tortoise.contrib.fastapi import register_tortoise
from fast_tmp.conf import settings
from fast_tmp.admin.register import register_static_service
from fast_tmp.site import register_model_site
from fast_tmp.factory import create_app

app = create_app()
app.title = "{{cookiecutter.project_slug}}"

register_tortoise(app, config=settings.TORTOISE_ORM)
if settings.DEBUG:
    register_static_service(app)

if __name__ == "__main__":
    import uvicorn  # type:ignore

    uvicorn.run(app, port=8000, lifespan="on")
