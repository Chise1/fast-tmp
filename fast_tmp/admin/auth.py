from datetime import timedelta
from typing import Any, Optional

from fastapi import Body, Cookie, Depends, FastAPI
from jose import JWTError
from starlette.responses import Response

from fast_tmp.admin.res_model import AmisRes
from fast_tmp.conf import settings
from fast_tmp.depends.auth import authenticate_user, get_user
from fast_tmp.models import User
from fast_tmp.responses import amis_credentials_exception as credentials_exception
from fast_tmp.responses import no_permission_exception
from fast_tmp.utils.token import create_access_token, decode_access_token


def app_add_login_url(
    app: FastAPI,
):
    """
    注册权限认证路由
    """
    assert settings.ADMIN_LOGIN_URL, "ADMIN_LOGIN_URL can't be None!"

    @app.post(settings.ADMIN_LOGIN_URL)
    async def login(
        response: Response,
        username: str = Body(
            ...,
        ),
        password: str = Body(
            ...,
        ),
    ):
        """
        admin登录页面
        """
        user = await authenticate_user(username, password)
        if not user:
            raise credentials_exception
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "id": user.pk}, expires_delta=access_token_expires
        )
        response.set_cookie(key="amisT", value=access_token)
        return AmisRes()


async def get_current_user(amisT: Optional[str] = Cookie(None)):
    if not amisT:
        raise credentials_exception
    try:
        payload = decode_access_token(amisT)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    获取活跃用户
    """

    if not current_user.is_active:
        raise no_permission_exception
    return current_user


async def get_superuser(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise credentials_exception
    return current_user


def get_user_has_perms(*perms: Any):
    """
    判定用户是否具有相关权限
    """

    async def user_has_perms(user: User = Depends(get_current_active_user)):

        if not perms or await user.has_perms(perms):
            return user
        else:
            raise no_permission_exception

    return user_has_perms
