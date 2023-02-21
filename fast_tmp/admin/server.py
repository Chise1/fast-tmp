import os
from datetime import timedelta
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from tortoise.exceptions import BaseORMException

from fast_tmp.admin.site import GroupAdmin, OperateRecordAdmin, PermissionAdmin, UserAdmin, UserInfo
from fast_tmp.conf import settings
from fast_tmp.exceptions import FastTmpError, NoAuthError
from fast_tmp.models import OperateRecord, Permission, User
from fast_tmp.responses import AdminRes
from fast_tmp.site import model_list, register_model_site
from fast_tmp.utils.token import create_access_token

from ..jinja_extension.tags import register_tags
from .depends import get_staff
from .endpoint import router
from .exception_handlers import (
    auth_exception_handler,
    fasttmp_exception_handler,
    tortoise_exception_handler,
)

base_path = os.path.dirname(__file__)
templates = Jinja2Templates(directory=base_path + "/templates")
register_tags(templates)
admin = FastAPI(title="fast-tmp")
register_model_site(
    {
        "Auth": [
            OperateRecordAdmin(),
            UserAdmin(),
            GroupAdmin(),
            PermissionAdmin(),
            UserInfo(prefix="self", label="self"),
        ]
    }
)
admin.include_router(router)
admin.exception_handler(NoAuthError)(auth_exception_handler)
admin.exception_handler(FastTmpError)(fasttmp_exception_handler)
admin.exception_handler(BaseORMException)(tortoise_exception_handler)


@admin.post("/", name="index", dependencies=[Depends(get_staff)])
@admin.get("/", name="index", dependencies=[Depends(get_staff)])
async def index(request: Request):
    user = request.user
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": admin.title,
            "api": "/admin/site",
            "avatar": user.avatar,
            "name": user.name,
        },
    )


@admin.post("/login", name="login")
async def login(
    request: Request,
    background_task: BackgroundTasks,
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
    user = await User.filter(username=username, is_staff=True, is_active=True).first()
    if not user or not user.check_password(password) or not user.is_active:
        context["errinfo"] = "username or password error!"
        return templates.TemplateResponse("login.html", context)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.pk},
        expires_delta=access_token_expires,
    )
    res = RedirectResponse(
        request.url_for("admin:index"),
        status_code=status.HTTP_302_FOUND,
    )
    res.set_cookie("access_token", access_token, expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    background_task.add_task(OperateRecord.login, user)
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


@admin.get("/site", dependencies=[Depends(get_staff)])
async def get_site(request: Request):
    pages = []
    index_page = None
    user = request.user
    if not user.is_superuser:
        perms = [
            i.codename
            for i in await Permission.filter(groups__users=user, codename__endswith="list")
        ]
        for name, ml in model_list.items():
            ml_p = []
            for model in ml:
                if model.prefix + "_list" in perms:
                    if not index_page:
                        index_page = model
                    ml_p.append(model)
            if len(ml_p) == 0:
                continue
            pages.append(
                {
                    "label": name,
                    "children": [model.site for model in ml_p],
                }
            )
        if index_page:
            pages.insert(0, {"label": index_page.name, "url": "/", "redirect": index_page.prefix})
    else:
        for name, ml in model_list.items():
            ml_p = []
            for model in ml:
                if not index_page:
                    index_page = model
                ml_p.append(model)
            if len(ml_p) == 0:
                continue
            pages.append(
                {
                    "label": name,
                    "children": [model.site for model in ml],
                }
            )
        if index_page:
            pages.insert(0, {"label": index_page.name, "url": "/", "redirect": index_page.prefix})
    return AdminRes(data={"pages": pages})
