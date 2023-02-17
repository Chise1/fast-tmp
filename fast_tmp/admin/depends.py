import datetime
import time
from typing import Optional

from fastapi import Cookie, Depends
from starlette.requests import Request

from fast_tmp.exceptions import NoAuthError
from fast_tmp.models import User
from fast_tmp.utils.token import decode_access_token


async def active_user_or_none(access_token: Optional[str] = Cookie(None)) -> Optional[User]:
    """
    获取active为true的用户，否则返回none
    """
    if access_token is not None:
        try:
            payload = decode_access_token(access_token)
            username: str = payload["sub"]
            create_time = payload["create_time"]
            if username is None:
                return None
        except Exception:
            return None
        user = await User.filter(username=username).first()
        if (
            user is not None
            and user.is_active
            and payload["exp"] >= datetime.datetime.now().timestamp()
            and user.update_time.timestamp() <= create_time
        ):
            return user
    return None


async def get_staff(request: Request, user: Optional[User] = Depends(active_user_or_none)):
    """
    found user and write to request
    """
    if not user or not user.is_staff:
        raise NoAuthError()
    request.scope["user"] = user
