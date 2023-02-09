from typing import Any, Optional

from pydantic import BaseModel

from fast_tmp.amis.base import SchemaNode


class CardHeader(BaseModel):
    title: str
    subTitle: str
    description: str
    avatarClassName: Optional[str]
    avatar: str


class Card(SchemaNode):
    """
    卡片
    https://aisuda.bce.baidu.com/amis/zh-CN/components/card
    """

    type: str = "card"
    header: CardHeader
    body: Any
