import os
from typing import Optional

from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from .router import router
from datetime import timedelta

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from fast_tmp.db import get_db_session
from fast_tmp.admin.depends import authenticate_user, decode_access_token_from_data
from fast_tmp.conf import settings
from fast_tmp.utils.token import create_access_token
from fast_tmp.admin.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.LOGIN_URL)
base_path = os.path.dirname(__file__)
templates = Jinja2Templates(directory=base_path + "/templates")

admin = FastAPI(title="后台")

admin.mount("/statics", app=StaticFiles(directory=base_path + "/statics"), name="statics")

# todo:增删改查，retrieve,destoryMany,
admin.include_router(router)


@admin.route("/index", name="index", methods=["GET", "POST"])
async def page(request: Request, user: Optional[User] = Depends(decode_access_token_from_data)):
    if not user:
        return RedirectResponse(
            "admin:login"
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@admin.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...),
                session: Session = Depends(get_db_session)):
    context = {
        "request": request,
        "errinfo": "",
        "username_err": False,
        "password_err": False,
    }
    if not username:
        context["username_err"] = True
        return templates.TemplateResponse("login.html", context)
    if not password:
        context["password_err"] = True
        return templates.TemplateResponse("login.html", context)

    user = authenticate_user(username, password, session)
    if not user:
        context["errinfo"] = "e"
        return templates.TemplateResponse("login.html", context)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
    )
    res = RedirectResponse(
        request.url_for(
            "admin:index",
        ),
    )
    res.set_cookie("access_token", access_token, expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return res


@admin.get("/login", name="login")
async def login_html(request: Request):
    context = {
        "request": request,
        "errinfo": "",
        "username_err": False,
        "password_err": False,
    }
    return templates.TemplateResponse("login.html", context)
