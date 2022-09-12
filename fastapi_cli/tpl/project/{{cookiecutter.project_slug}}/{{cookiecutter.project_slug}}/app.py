import os

from tortoise.contrib.fastapi import register_tortoise

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", '{{cookiecutter.project_slug}}.settings')
from fast_tmp.factory import create_app
from fast_tmp.conf import settings

app = create_app()
register_tortoise(app, config=settings.TORTOISE_ORM)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
