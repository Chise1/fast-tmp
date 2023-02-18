from typing import Any, Optional, Tuple, Union

from pydantic import BaseModel


class BadgeSchema(BaseModel):
    mode: str  # 角标类型，可以是 dot/text/ribbon
    text: Optional[Union[str, int]]
    size: Optional[int]
    level: Optional[str]  # 角标级别, 可以是 info/success/warning/danger, 设置之后角标背景颜色不同
    overflowCount: Optional[int]  # 设置封顶的数字值
    position: Optional[str]  # 角标位置， 可以是 top-right/top-left/bottom-right/bottom-left
    offset: Optional[Tuple[int, int]]  # 角标位置，offset 相对于 position 位置进行水平、垂直偏移
    className: Optional[str]
    animation: Optional[bool]  # 角标是否显示动画
    style: Optional[Any]  # 角标的自定义样式
    visibleOn: Optional[Any]  # 控制角标的显示隐藏
