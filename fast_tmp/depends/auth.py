from datetime import timedelta
from typing import Any, Optional, Tuple

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError

from fast_tmp.conf import settings
from fast_tmp.models import User
from fast_tmp.utils.token import create_access_token, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.LOGIN_URL)


def register_app(app: FastAPI):
    """
    注册权限认证路由
    """

    @app.post(settings.LOGIN_URL)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        """
        仅用于docs页面测试返回用
        """
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "id": user.pk}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}


async def get_user(username: str) -> Optional[User]:
    user = await User.filter(username=username).first()
    return user


async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    验证密码
    """
    user = await get_user(username)
    if not user:
        return None
    if not user.verify_password(password):
        return None
    return user


async def authenticate_active_user(username: str, password: str) -> Optional[User]:
    """
    验证密码
    """
    user = await get_user(username)
    if not user or not user.is_active or not user.verify_password(password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user_or_none(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    获取active为true的用户，否则返回none
    """
    print("1")
    try:
        print("2")

        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        print("1")
        return None
    user = await get_user(username=username)
    if user is not None and user.is_active:
        return user
    print("4")

    return None


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    获取活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_superuser(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user


def get_user_has_perms(perms: Optional[Tuple[Any, ...]]):
    """
    判定用户是否具有相关权限
    """

    async def user_has_perms(user: User = Depends(get_current_active_user)):

        if not perms or await user.has_perms(perms):
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no permissions.",
            )

    return user_has_perms
