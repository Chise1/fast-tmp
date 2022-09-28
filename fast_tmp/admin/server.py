import os
from datetime import timedelta
from typing import Optional

from fastapi import Depends, FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from tortoise.exceptions import BaseORMException

from fast_tmp.admin.site import GroupAdmin, PermissionAdmin, UserAdmin
from fast_tmp.conf import settings
from fast_tmp.models import Permission, User
from fast_tmp.responses import BaseRes, FastTmpError
from fast_tmp.site import model_list, register_model_site
from fast_tmp.utils.token import create_access_token

from ..jinja_extension.tags import register_tags
from .depends import get_staff
from .endpoint import router
from .exception_handlers import fasttmp_exception_handler, tortoise_exception_handler

base_path = os.path.dirname(__file__)
templates = Jinja2Templates(directory=base_path + "/templates")
register_tags(templates)
admin = FastAPI(title="fast-tmp")
register_model_site({"Auth": [UserAdmin(), GroupAdmin(), PermissionAdmin()]})
admin.include_router(router)

admin.exception_handler(FastTmpError)(fasttmp_exception_handler)
admin.exception_handler(BaseORMException)(tortoise_exception_handler)


@admin.post("/", name="index", dependencies=[Depends(get_staff)])
@admin.get("/", name="index", dependencies=[Depends(get_staff)])
async def index(request: Request):
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
    user = await User.filter(username=username, is_staff=True, is_active=True).first()
    if not user or not user.check_password(password) or not user.is_active:
        context["errinfo"] = "username or password error!"
        return templates.TemplateResponse("login.html", context)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.pk}, expires_delta=access_token_expires
    )
    res = RedirectResponse(
        request.url_for("admin:index"),
        status_code=status.HTTP_302_FOUND,
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


@admin.get("/site", dependencies=[Depends(get_staff)])
async def get_site(request: Request):
    pages = []
    user = request.user
    if not user.is_superuser:
        perms = [
            i.codename
            for i in await Permission.filter(groups__users=user, codename__endswith="list")
        ]
    else:
        perms = [i.codename for i in await Permission.filter(codename__endswith="list")]
    for name, ml in model_list.items():  # todo add home page
        ml_p = []
        for model in ml:
            if model.name + "_list" in perms:
                ml_p.append(model)
        if len(ml_p) == 0:
            continue
        pages.append(  # todo 增加权限控制，确认对应的页面
            {
                "label": name,
                "children": [
                    {
                        "label": model.name,
                        "url": model.prefix,
                        "schemaApi": model.prefix + "/schema",
                    }
                    for model in ml
                ],
            }
        )
    return BaseRes(data={"pages": pages})
