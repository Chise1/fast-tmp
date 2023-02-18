from typing import List, Optional

from .base import SchemaNode


class Grid(SchemaNode):
    type = "grid"
    className: Optional[str]
    gap: Optional[str]  # 'xs' | 'sm' | 'base' | 'none' | 'md' | 'lg'
    valign: Optional[str]  # 'top' | 'middle' | 'bottom' | 'between'
    align: Optional[str]  # 'left' | 'right' | 'between' | 'center'
    columns: List[SchemaNode]
