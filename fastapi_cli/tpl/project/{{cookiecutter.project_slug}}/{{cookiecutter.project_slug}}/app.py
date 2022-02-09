import os
from fastapi import FastAPI

from fast_tmp.admin.server import admin

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", '{{cookiecutter.project_slug}}.settings')
from fast_tmp.site import register_model_site

app =FastAPI(title='{{cookiecutter.project_slug}}')
app.mount("/admin", admin, name="admin", )

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
