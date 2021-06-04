from datetime import timedelta

from fastapi import Body, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from ..conf import settings
from ..depends.auth import authenticate_user
from ..utils.token import create_access_token
from .router import router

templates = Jinja2Templates(directory="templates")

admin = FastAPI(title="后台")
admin.mount("/static", StaticFiles(directory="static"), name="static")

# todo:增删改查，retrieve,destoryMany,
admin.include_router(router)


@admin.get("/index", response_class=HTMLResponse)
async def page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


# todo:增加登陆接口
@admin.post("/login")
async def login(
    username: str = Body(
        ...,
    ),
    password: str = Body(
        ...,
    ),
):
    """登陆"""
    user = await authenticate_user(username, password)
    if not user:
        return {"status": 401, "msg": "未登陆或登陆已过期", "data": {}}
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "id": user.pk}, expires_delta=access_token_expires
        )
        return {"status": 0, "msg": "", "data": {"access_token": access_token}}
