from typing import Optional

from fast_tmp.amis.forms import Column, ControlEnum


class Custom(Column):
    # label:str
    # name:Optional[str]
    type = ControlEnum.custom
    onMount: Optional[str]
    onUpdate: Optional[str]
    onUnmount: Optional[str]
    html: Optional[str]
    inline: Optional[bool]
    id: Optional[str]
