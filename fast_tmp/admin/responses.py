from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.status import HTTP_303_SEE_OTHER


def redirect(request: Request, view: str, **params):
    return RedirectResponse(
        url=request.app.admin_path + request.app.url_path_for(view, **params),
        status_code=HTTP_303_SEE_OTHER,
    )


Admin401Error = JSONResponse(
    status_code=200,
    content={"status": 401, "msg": "用户认证失败",
             "data": {}})
