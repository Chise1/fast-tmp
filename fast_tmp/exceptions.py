from typing import Optional

from fastapi import HTTPException

from fast_tmp.responses import BaseRes


class FastTmpError(HTTPException):
    status_code = 200

    def __init__(self, content: str):
        self.detail = BaseRes(status=400, msg=content).json()


class NoAuthError(HTTPException):
    def __init__(self):
        self.status_code = 302
        self.detail = BaseRes(msg="please sign in ").json()


class TmpValueError(FastTmpError):
    def __init__(self, content: str):
        self.detail = BaseRes(status=400, msg=content or "field vale is error").json()


class NotFoundError(FastTmpError):
    def __init__(self, content: Optional[str] = None):
        self.detail = BaseRes(status=400, msg=content or "not found model").json()
