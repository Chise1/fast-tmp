from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

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
