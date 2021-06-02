from fastapi import FastAPI
from .router import router

admin = FastAPI(title="后台")
# todo:增删改查，retrieve,destoryMany,
admin.include_router(router)
