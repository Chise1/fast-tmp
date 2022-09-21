from requests import Request
from fastapi.responses import JSONResponse

from fast_tmp.responses import BaseRes


async def check_error_middle(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        response = JSONResponse(content=BaseRes(msg=str(e), status=400).json())
    return response
