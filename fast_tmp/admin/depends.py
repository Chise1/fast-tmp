from typing import Optional

from fastapi import Depends, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND
from tortoise import Tortoise


def get_model(resource: Optional[str]):
    if not resource:
        return
    for app, models in Tortoise.apps.items():
        model = models.get(resource)
        if model:
            return model


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
