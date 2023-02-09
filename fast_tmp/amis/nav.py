from pydantic.main import BaseModel

from fast_tmp.amis.base import SchemaNode


class NavLinks(BaseModel):
    label: str
    to: str


class Nav(SchemaNode):
    type = "nav"
    stacked: bool = True
    className: str = "w-md"
