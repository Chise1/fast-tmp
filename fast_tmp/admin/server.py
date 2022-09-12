import os
from datetime import timedelta
from typing import Optional

from fastapi import Depends, FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from fast_tmp.conf import settings
from fast_tmp.models import User
from fast_tmp.responses import BaseRes
from fast_tmp.site import model_list, register_model_site
from fast_tmp.utils.token import create_access_token
from .depends import __get_user_or_none
from ..jinja_extension.tags import register_tags
from .endpoint import router
from fast_tmp.admin.site import UserAdmin, GroupAdmin

base_path = os.path.dirname(__file__)
templates = Jinja2Templates(directory=base_path + "/templates")
register_tags(templates)
admin = FastAPI(title="fast-tmp")
register_model_site({"Auth": [UserAdmin, GroupAdmin]})
admin.include_router(router)


@admin.post("/", name="index")
@admin.get("/", name="index")
async def index(request: Request, user: Optional[User] = Depends(__get_user_or_none)):
    if not user:
        return RedirectResponse(request.url_for("admin:login"))
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": admin.title},
    )


@admin.post("/login", name="login")
async def login(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
):
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
    user = await User.get(username=username)
    if not user or not user.verify_password(password) or not user.is_active:
        context["errinfo"] = "username or password error!"
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
def login_html(request: Request):
    print("...........")
    context = {
        "request": request,
        "errinfo": "",
        "username_err": False,
        "password_err": False,
    }
    return templates.TemplateResponse("login.html", context)


@admin.get("/logout", name="logout")
def logout(request: Request):
    context = {
        "request": request,
        "errinfo": "",
        "username_err": False,
        "password_err": False,
    }
    res = templates.TemplateResponse("login.html", context)
    res.delete_cookie("access_token")
    return res


@admin.get("/site")
def get_site(request: Request, user: Optional[User] = Depends(__get_user_or_none)):
    if not user:
        return RedirectResponse(request.url_for("admin:login"))
    pages = []
    for name, ml in model_list.items():  # todo add home page
        pages.append(  # todo 增加权限控制，确认对应的页面
            {
                "label": name,
                "children": [
                    {
                        "label": model.name(),
                        "url": model.name(),
                        "schemaApi": model.name() + "/schema",
                    }
                    for model in ml
                ],
            }
        )
    return BaseRes(data={"pages": pages})
