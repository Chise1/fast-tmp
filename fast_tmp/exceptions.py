from typing import Dict, Optional

from fastapi import HTTPException

from fast_tmp.responses import BaseRes, FieldErrorRes


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


class PermError(FastTmpError):
    def __init__(self, content: Optional[str] = None):
        self.detail = BaseRes(status=400, msg=content or "you have no permission").json()


class FieldsError(FastTmpError):
    """
    返回给amis的字段校验错误认证
    """

    def __init__(self, error_info: Dict[str, str]):
        self.detail = FieldErrorRes(errors=error_info).json()
