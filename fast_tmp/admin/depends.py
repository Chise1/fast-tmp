from typing import Optional

from fastapi import Depends, HTTPException, Cookie
from jose import JWTError
from sqlalchemy import select
from sqlmodel import Session
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from fast_tmp.db import get_db_session
from fast_tmp.exceptions import credentials_exception, password_exception
from fast_tmp.models import User
from fast_tmp.utils.token import decode_access_token


def get_model(resource: str):

    return None
    # for app, models in Tortoise.apps.items():
    #     model = models.get(resource)
    #     if model:
    #         return model
    # else:
    #     raise Exception("not found module")


async def get_model_resource(request: Request, model=Depends(get_model)):
    model_resource = request.app.get_model_resource(model)
    if not model_resource:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    actions = await model_resource.get_actions(request)
    bulk_actions = await model_resource.get_bulk_actions(request)
    toolbar_actions = await model_resource.get_toolbar_actions(request)
    compute_fields = await model_resource.get_compute_fields(request)
    setattr(model_resource, "toolbar_actions", toolbar_actions)
    setattr(model_resource, "actions", actions)
    setattr(model_resource, "bulk_actions", bulk_actions)
    setattr(model_resource, "compute_fields", compute_fields)
    return model_resource


def decode_access_token_from_data(access_token: Optional[str] = Cookie(None),
                                  session: Session = Depends(get_db_session)) -> Optional[User]:
    if access_token is not None:
        try:
            payload = decode_access_token(access_token)
            username: str = payload.get("sub")
            if username:
                user: User = get_user(username, session)
                if user:
                    return user
        except JWTError:
            pass
    return None


def get_user(username: str, session: Session) -> User:
    res = session.execute(select(User).where(User.username == username, User.is_active == True))
    return res.scalar_one_or_none()


def authenticate_user(username: str, password: str, session: Session) -> Optional[User]:
    """
    验证密码
    """
    user = get_user(username, session)
    if user and user.verify_password(password):
        return user
    return None
