import os
from fastapi import FastAPI

from fast_tmp.db import engine
from fast_tmp.models import Base

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", 'settings')
from fast_tmp.admin.server import admin
from example.factory import create_app
from fast_tmp.site import register_model_site
from example.admin import UserInfoAdmin

register_model_site({"Example":[UserInfoAdmin]})
app: FastAPI = create_app()
app.mount("/admin", admin, name="admin", )
# Base.metadata.create_all(engine)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, lifespan="on")
