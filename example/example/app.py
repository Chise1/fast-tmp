import os
from fastapi import FastAPI

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", 'settings')
from fast_tmp.admin.server import admin
from example.factory import create_app

app: FastAPI = create_app()
app.mount("/admin", admin, name="admin", )
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True, port=8000, lifespan="on")
