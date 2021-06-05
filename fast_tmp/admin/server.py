from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from fast_tmp.conf import settings

from .auth import app_add_login_url
from .router import router

admin = FastAPI(title="后台")
admin.include_router(router)

app_add_login_url(admin)

if settings.DEBUG:
    templates = Jinja2Templates(directory="templates")
    admin.mount("/static", StaticFiles(directory="static"), name="static")

    @admin.get("/index", response_class=HTMLResponse)
    async def page(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
            },
        )
