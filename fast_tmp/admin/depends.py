from typing import Optional

from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_tmp.db import get_db_session
from fast_tmp.models import User
from fast_tmp.utils.token import decode_access_token


def decode_access_token_from_data(
    access_token: Optional[str] = Cookie(None), session: Session = Depends(get_db_session)
) -> Optional[User]:
    if access_token is not None:
        try:
            payload = decode_access_token(access_token)
            username: str = payload.get("sub")
            if username:
                user = get_user(username, session)
                if user:
                    return user
        except Exception:  # nosec
            pass
    return None


def get_user(username: str, session: Session) -> Optional[User]:
    res = session.execute(
        select(User)  # type: ignore
        .where(User.username == username)
        .where(User.is_active == True)  # noqa
    )

    return res.scalar_one_or_none()  # type: ignore


def authenticate_user(username: str, password: str, session: Session) -> Optional[User]:
    """
    验证密码
    """
    user = get_user(username, session)
    if user and user.verify_password(password):
        return user
    return None
