# 一条横线
from pydantic import BaseModel


class Divider(BaseModel):
    """
    一条横线
    """

    type: str = "divider"
