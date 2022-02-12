import os
from datetime import timedelta
from typing import Optional

from fastapi import Depends, FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from fast_tmp.admin.depends import authenticate_user, decode_access_token_from_data
from fast_tmp.conf import settings
from fast_tmp.db import get_db_session
from fast_tmp.models import User
from fast_tmp.models.site import GroupAdmin, UserAdmin
from fast_tmp.responses import BaseRes
from fast_tmp.site import model_list, register_model_site
from fast_tmp.utils.token import create_access_token

from ..jinja_extension.tags import register_tags
from .constant import crud_root_rooter, model_router
from .endpoint import router

base_path = os.path.dirname(__file__)
templates = Jinja2Templates(directory=base_path + "/templates")
register_tags(templates)
admin = FastAPI(title="fast-tmp")
if settings.LOCAL_STATIC:
    admin.mount("/static", app=StaticFiles(directory=os.getcwd() + "/static"), name="static")
else:
    admin.mount("/static", app=StaticFiles(directory=base_path + "/static"), name="static")

register_model_site({"Auth": [UserAdmin, GroupAdmin]})
admin.include_router(router, prefix=model_router)


@admin.get(
    "/",
    name="index",
)
def index(request: Request, user: Optional[User] = Depends(decode_access_token_from_data)):
    if not user:
        return RedirectResponse(request.url_for("admin:login"))
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": admin.title},
    )


@admin.post(
    "/",
    name="index",
)  # bug:can not use admin.route .It can't check depends.
def index_post(request: Request, user: Optional[User] = Depends(decode_access_token_from_data)):
    if not user:
        return RedirectResponse(request.url_for("admin:login"))

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": admin.title},
    )


@admin.post("/login")
def login(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    session: Session = Depends(get_db_session),
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
def login_html(request: Request):
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
def get_site(request: Request, user: Optional[User] = Depends(decode_access_token_from_data)):
    if not user:
        return RedirectResponse(request.url_for("admin:login"))
    pages = []
    for name, ml in model_list.items():  # todo add home page
        pages.append(
            {
                "label": name,
                "children": [
                    {
                        "label": model.name(),
                        "url": model.name(),
                        "schemaApi": crud_root_rooter + model.name() + "/schema",
                    }
                    for model in ml
                ],
            }
        )
    return BaseRes(data={"pages": pages})
