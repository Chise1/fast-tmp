from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from tortoise.exceptions import BaseORMException

from fast_tmp.responses import BaseRes, FastTmpError, NoAuthError


async def fasttmp_exception_handler(request: Request, exc: FastTmpError):
    return JSONResponse(
        status_code=200,
        content=exc.detail,
    )


async def tortoise_exception_handler(request: Request, exc: BaseORMException):
    return JSONResponse(content=BaseRes(msg=str(exc), status=400).dict(), status_code=200)


async def no_auth_middle(request: Request, call_next):
    try:
        response = await call_next(request)
    except NoAuthError:
        return RedirectResponse(request.url_for("admin:login"))
    return response
