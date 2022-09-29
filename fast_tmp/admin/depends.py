from typing import Optional

from fastapi import Cookie, Depends, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND
from tortoise import Tortoise

from fast_tmp.exceptions import NoAuthError
from fast_tmp.models import User

# todo 需要判定是否存在对应的权限字段，如果没有则写入
from fast_tmp.utils.token import decode_access_token


def get_model(resource: str):
    for app, models in Tortoise.apps.items():
        model = models.get(resource)
        if model:
            return model
    else:
        raise Exception("not found module")


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


async def __get_user_or_none(access_token: Optional[str] = Cookie(None)) -> Optional[User]:
    """
    获取active为true的用户，否则返回none
    """
    if access_token is not None:
        try:
            payload = decode_access_token(access_token)
            username: str = payload.get("sub")
            if username is None:
                return None
        except Exception:
            return None
        return await User.filter(username=username).first()
    return None


async def get_staff(request: Request, user: Optional[User] = Depends(__get_user_or_none)):
    """
    found user and write to request
    """
    if not user or not user.is_active or not user.is_staff:
        raise NoAuthError()
    request.scope["user"] = user
