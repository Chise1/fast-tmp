from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fast_tmp.responses import BaseRes, NoAuthError


async def check_error_middle(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        response = JSONResponse(content=BaseRes(msg=str(e), status=400).json())
    return response


async def no_auth_middle(request: Request, call_next):
    try:
        response = await call_next(request)
    except NoAuthError:
        return RedirectResponse(request.url_for("admin:login"))
    return response
