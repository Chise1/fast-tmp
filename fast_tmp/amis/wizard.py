from typing import List, Optional

from pydantic import BaseModel

from fast_tmp.amis.base import SchemaNode
from fast_tmp.amis.formitem import FormItem


class WizardStep(BaseModel):
    type: Optional[str] = None
    title: str  # 步骤标题
    mode: Optional[str]  # 展示默认，跟 Form 中的模式一样，选择： normal、horizontal或者inline。
    api: Optional[str]  # 最后一步保存的接口。
    initApi: Optional[str]  # 初始化数据接口
    initFetch: Optional[bool]  # 初始是否拉取数据。
    initFetchOn: Optional[str]  # 初始是否拉取数据，通过表达式来配置
    body: List[FormItem]  # 当前步骤的表单项集合，请参考 FormItem。


class Wizard(SchemaNode):
    """
    表单向导，能够配置多个步骤引导用户一步一步完成表单提交。
    https://aisuda.bce.baidu.com/amis/zh-CN/components/wizard
    """

    type = "wizard"
    mode: Optional[str]  # horizontal 或者 vertical
    api: Optional[str]  # 最后一步保存的接口。
    initApi: Optional[str]  # 初始化数据接口
    initFetch: Optional[bool]  # 初始是否拉取数据。
    initFetchOn: Optional[str]  # 初始是否拉取数据，通过表达式来配置
    actionPrevLabel: Optional[str]  # 上一步按钮文本
    actionNextLabel: Optional[str]  # 下一步按钮文本
    actionNextSaveLabel: Optional[str]  # 保存并下一步按钮文本
    actionFinishLabel: Optional[str]  # 完成按钮文本
    className: Optional[str]  # 外层 CSS 类名
    actionClassName: Optional[str]  # 按钮 CSS 类名
    reload: Optional[str]  # 操作完后刷新目标对象。请填写目标组件设置的 name 值，如果填写为 window 则让当前页面整体刷新。
    redirect: Optional[str]  # 操作完后跳转。
    target: Optional[
        str
    ]  # 可以把数据提交给别的组件而不是自己保存。请填写目标组件设置的 name 值，如果填写为 window 则把数据同步到地址栏上，同时依赖这些数据的组件会自动重新刷新。
    steps: List[WizardStep]  # Array < step > 数组，配置步骤信息
    startStep: Optional[
        int
    ]  # 起始默认值，从第几步开始。可支持模版，但是只有在组件创建时渲染模版并设置当前步数，在之后组件被刷新时，当前 step 不会根据 startStep 改变
