from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from tortoise.exceptions import BaseORMException

from fast_tmp.responses import BaseRes, FastTmpError, NoAuthError


async def fasttmp_exception_handler(request: Request, exc: FastTmpError):
    if isinstance(exc, NoAuthError):
        return RedirectResponse(request.url_for("admin:login"), status_code=status.HTTP_302_FOUND)
    return Response(
        status_code=200, content=exc.detail, headers={"Content-Type": "appliation/json"}
    )


async def tortoise_exception_handler(request: Request, exc: BaseORMException):
    return JSONResponse(content=BaseRes(msg=str(exc), status=400).dict(), status_code=200)
