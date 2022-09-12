from typing import List, Union

from fast_tmp.admin.schema.abstract_schema import BaseAmisModel, _Action
from fast_tmp.admin.schema.buttons import Operation
from fast_tmp.admin.schema.enums import TypeEnum
from fast_tmp.admin.schema.forms import Column


class CRUD(BaseAmisModel):
    type = TypeEnum.crud
    api: str  # 相对路径
    # 可以在后面跟上按钮，则默认每一行都有按钮，
    # 参考：https://baidu.gitee.io/amis/docs/components/dialog?page=1
    columns: List[Union[Column, _Action, Operation]]
    affixHeader: bool = False

    class Config:
        arbitrary_types_allowed = True
