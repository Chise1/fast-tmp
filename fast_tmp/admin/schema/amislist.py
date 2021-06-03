from pydantic.main import BaseModel

from fast_tmp.admin.schema.enums import TypeEnum

from .crud import CRUD


class AmisList(BaseModel):
    type = TypeEnum.page
    body: CRUD
