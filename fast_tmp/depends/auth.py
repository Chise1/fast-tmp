from typing import Any, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from fast_tmp.conf import settings
from fast_tmp.models import User
from fast_tmp.utils.token import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.FAST_TMP_URL + "/auth/token")


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


def get_user_has_perms(perms: List[Any]):
    """
    判定用户是否具有相关权限
    """

    async def user_has_perms(user: User = Depends(get_current_active_user)):
        if await user.has_perms(perms):
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return user_has_perms
