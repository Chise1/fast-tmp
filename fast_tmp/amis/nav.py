from pydantic.main import BaseModel

from fast_tmp.amis.base import BaseAmisModel

from .enums import TypeEnum


class NavLinks(BaseModel):
    label: str
    to: str


class Nav(BaseAmisModel):
    type = TypeEnum.nav
    stacked: bool = True
    className: str = "w-md"
