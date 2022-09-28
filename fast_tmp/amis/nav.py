from pydantic.main import BaseModel
from pydantic.networks import HttpUrl

from fast_tmp.amis.base import BaseAmisModel

from .enums import TypeEnum


class NavLinks(BaseModel):
    label: str
    to: HttpUrl


class Nav(BaseAmisModel):
    type = TypeEnum.nav
    stacked: bool = True
    className: str = "w-md"
