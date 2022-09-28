from typing import Any, Optional

from pydantic import BaseModel

from fast_tmp.amis.base import BaseAmisModel


class CardHeader(BaseModel):
    title: str
    subTitle: str
    description: str
    avatarClassName: Optional[str]
    avatar: str


class Card(BaseAmisModel):
    type: str = "card"
    header: CardHeader
    body: Any
