from pydantic.main import BaseModel

from fast_tmp.amis.base import BaseAmisModel


class NavLinks(BaseModel):
    label: str
    to: str


class Nav(BaseAmisModel):
    type = "nav"
    stacked: bool = True
    className: str = "w-md"
