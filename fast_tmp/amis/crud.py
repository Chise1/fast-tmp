from typing import List, Optional, Union

from fast_tmp.amis.base import BaseAmisModel, _Action
from fast_tmp.amis.column import Column, Operation
from fast_tmp.amis.forms import FilterModel


class CRUD(BaseAmisModel):
    type = "crud"
    api: str  # 相对路径
    # 可以在后面跟上按钮，则默认每一行都有按钮，
    # 参考：https://baidu.gitee.io/amis/docs/components/dialog?page=1
    columns: List[Union[Column, _Action, Operation]]
    affixHeader: bool = False
    quickSaveItemApi: Optional[str]  # 快速保存
    syncLocation: Optional[bool]
    filter: Optional[FilterModel]

    class Config:
        arbitrary_types_allowed = True
