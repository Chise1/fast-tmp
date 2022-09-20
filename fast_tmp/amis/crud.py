from typing import List, Union, Optional

from fast_tmp.amis.abstract_schema import BaseAmisModel, _Action
from fast_tmp.amis.buttons import Operation
from fast_tmp.amis.enums import TypeEnum
from fast_tmp.amis.forms import Column


class CRUD(BaseAmisModel):
    type = TypeEnum.crud
    api: str  # 相对路径
    # 可以在后面跟上按钮，则默认每一行都有按钮，
    # 参考：https://baidu.gitee.io/amis/docs/components/dialog?page=1
    columns: List[Union[Column, _Action, Operation]]
    affixHeader: bool = False
    quickSaveItemApi: Optional[str]  # 快速保存

    class Config:
        arbitrary_types_allowed = True
