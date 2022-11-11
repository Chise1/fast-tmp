# -*- encoding: utf-8 -*-
"""
@File    : control.py
@Time    : 2022/11/9 12:15
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from .column import AbstractControl, Column, SelectOption
from .forms import Form
from .style import FormWidgetSize, Mode


class FormItemEnum(str, Enum):
    form = "form"  # 表单
    button_group_select = "button-group-select"  # 按钮点选
    chained_select = "chained-select"  # 链式下拉框
    chart_radios = "chart-radios"  # 图表单选框
    checkbox = "checkbox"  # 勾选框
    checkboxes = "checkboxes"  # 复选框
    combo = "combo"  # 组合
    input_kv = "input-kv"  # 键值对
    array = "array"
    input_array = "input-array"  # 数组输入框
    input_city = "input-city"  # 城市选择器
    input_color = "input-color"  # 颜色选择器
    input_date = "input-date"  # 日期选择器
    input_date_range = "input-date-range"  # 日期范围选择器
    date = "date"
    time = "time"
    uuid = "uuid"
    input_rich_text = "input-rich-text"
    input_datetime = "input-datetime"
    input_datetime_range = "input-datetime-range"  # 日期时间选择器
    input_time_range = "input-time-range"  # 时间范围选择器
    input_group = "input-group"  # 输入框组合
    input_month_range = "input-month-range"  # 月份范围
    input_number = "input-number"  # 数字输入
    input_quarter_range = "input-quarter-range"  # 季度范围
    input_range = "input-range"  # 滑块
    input_rating = "input-rating"  # 评分
    input_tag = "input-tag"  # 标签选择器
    input_text = "input-text"  # 输入框
    input_password = "input-password"  # 密码输入框
    input_email = "input-email"  # 邮箱输入框
    input_url = "input-url"  # url = "url"输入框
    native_date = "native-date"  # native = "native"日期选择器
    native_time = "native-time"  # native = "native"时间选择器
    native_number = "native-number"  # native = "native"数字输入
    input_tree = "input-tree"  # 树形选择器
    input_year_range = "input-year-range"  # 年份范围
    list_select = "list-select"  # 列表选择器
    location_picker = "location-picker"  # 地理位置
    matrix_checkboxes = "matrix-checkboxes"  # 矩阵勾选
    nested_select = "nested-select"  # 级联选择器
    radios = "radios"  # 单选框
    select = "select"  # 下拉框
    multi_select = "multi-select"  # 多选下拉框
    switch = "switch"  # 开关
    tabs_transfer = "tabs-transfer"  # 组合穿梭器
    tabs_transfer_picker = "tabs-transfer-picker"  # 组合穿梭选择器
    textarea = "textarea"  # 多行输入框
    transfer = "transfer"  # 穿梭器
    transfer_picker = "transfer-picker"  # 穿梭选择器
    tree_select = "tree-select"  # 属性选择器
    input_image = "input-image"
    input_file = "input-file"
    picker = "picker"


class FormItem(AbstractControl):
    """
    用户form表单等写入
    """

    clearable: Optional[bool]
    value: Optional[Any]  # 默认值
    labelRemark: Optional[str]  # 表单项标签描述
    description: Optional[str]  # 描述
    placeholder: Optional[str]  # 描述
    inline: Optional[bool]  # 内联样式
    submitOnChange: Optional[bool]  # 是否该表单项值发生变化时就提交当前表单。
    disabled: Optional[bool]
    disableOn: Optional[str]  # 配置规则查看https://baidu.gitee.io/amis/docs/components/form/formitem
    visible: Optional[bool]
    visibleOn: Optional[str]  # 配置规则查看https://baidu.gitee.io/amis/docs/components/form/formitem
    required: Optional[bool]
    requiredOn: Optional[str]
    hidden: Optional[bool]  # 可使用条件配置如 this.number>1
    hiddenOn: Optional[str]  # 配置判定逻辑
    validations: Optional[Any]  # 注意，键值对请参考ValidateEnum
    validationErrors: Optional[
        Dict[str, str]  # todo tortoise-orm的校验转这里
    ]  # 注意，键值对请参考ValidateEnum，举例："minimum": "同学，最少输入$1以上的数字哈",其中$1为该错误的数据
    className: Optional[str]  # 表单最外层类名
    inputClassName: Optional[str]  # 表单控制器类名
    labelClassName: Optional[str]  # label 的类名
    mode: Optional[Mode]
    size: Optional[FormWidgetSize]

    class Config:
        orm_mode = True


class AddControl(BaseModel):
    type: str = "text"
    name: str
    label: str


class Item(BaseModel):
    label: str
    value: Union[str, int]


class ItemValidation(BaseModel):  # 验证工具
    pass


class ItemValidationError(BaseModel):
    pass


class NumberItem(FormItem):
    type: FormItemEnum = FormItemEnum.input_number
    min: Optional[int]
    max: Optional[int]
    precision: Optional[int]  # 小数点后几位
    step: Optional[int]  # 选择的步长
    value: Optional[int]
    showSteps: Optional[bool] = False
    big: Optional[bool]


class NativeNumber(FormItem):
    type: FormItemEnum = FormItemEnum.native_number


class SelectItem(FormItem):
    type: FormItemEnum = FormItemEnum.select
    options: Optional[Union[List[str], List[int], List[SelectOption]]]
    source: Optional[str]  # 通过数据源里面获取，也可以配置地址从远程获取，值格式为:options:[{label:..,value:...,}]
    # children: Optional[List[Union[SelectOption, str, int]]]  # 这个在树结构在考虑
    multiple: Optional[bool]  # 是否多选
    delimeter: Optional[str]
    labelField: Optional[str]
    valueField: Optional[str]
    joinValues: Optional[bool]
    extractValue: Optional[bool]
    checkAll: Optional[bool]  # 是否支持全选
    checkAllLabel: Optional[str]  # 全选的文字，默认为‘全选’
    defaultCheckAll: Optional[bool]  # 是否默认全选
    # 配置返回数组格式，具体参考https://baidu.gitee.io/amis/docs/components/form/
    # options#%E5%8A%A8%E6%80%81%E9%85%8D%E7%BD%AE
    searchable: Optional[bool]  # 前端对选项是否启动搜索功能
    autoComplete: Optional[bool]  # 是否对选项启动自动补全

    class Config:
        orm_mode = True


class SelectItemCanModifyItem(SelectItem):
    """
    可以修改选项值的选择器
    """

    creatable: bool = False  # 是否支持新增选项
    addControls: Tuple[AddControl, ...] = (
        AddControl(type="text", name="label", label="选项标题"),
        AddControl(type="text", name="value", label="选项值"),
    )  # 配置弹框信息，第一个为标题，第二个为选项值
    addApi: Optional[str]  # 配置增加接口，如果为空则不会保存
    editable: bool = False  # 前端是否可编辑
    editControls: Tuple[AddControl, ...] = (
        AddControl(type="text", name="label", label="选项标题"),
        AddControl(type="text", name="value", label="选项值"),
    )  # 配置修改值的弹框信息
    editApi: Optional[str]
    deleteApi: Optional[str]  # 配置删除接口


class ArrayItem(FormItem):
    type: FormItemEnum = FormItemEnum.array
    items: str = "text"  # 这个到时候改为枚举
    addable: bool = True  # 是否可新增
    removable: bool = True  # 是否可删除
    draggable: bool = False  # 是否可拖动排序，是否可以拖动排序, 需要注意的是当启用拖动排序的时候，
    # 会多一个$id 字段，具体请参考：https://baidu.gitee.io/amis/docs/components/form/array
    draggableTip: Optional[str]
    addButtonText: Optional[str]  # 新增按钮的文字
    minLength: Optional[int]  # 最短长度
    maxLength: Optional[int]  # 最长长度


class DatetimeItem(FormItem):
    type: FormItemEnum = FormItemEnum.input_datetime
    value: Optional[str]
    format: str = "YYYY-MM-DD HH:mm:ss"  # 'X'为时间戳格式,参考文档：
    # https://baidu.gitee.io/amis/zh-CN/docs/components/form/datetime
    inputFormat: str = "YYYY-MM-DD HH:mm:ss"  # 'X'为时间戳格式
    # shortcuts: List[str] = []  # "yesterday" ,"today", "tomorrow",now,{n}hoursago : n 小时前，例
    # 如：1daysago，下面用法相同,{n}hourslater : n 小时前，例如：1daysago
    utc: Optional[bool]
    embed: Optional[bool]

    # timeConstrainst: bool = True  # 不知道干吗用的

    class Config:
        orm_mode = True


class DateItem(FormItem):
    type = FormItemEnum.date
    value: Optional[str]
    format: str = "YYYY-MM-DD"  # 格式请参考文档：https://baidu.gitee.io/amis/zh-CN/docs/components/form/date  # 'X'为时间戳格式
    inputFormat: str = "YYYY-MM-DD"  # 'X'为时间戳格式
    # shortcuts: List[str] = []  # "yesterday" ,"today", "tomorrow"
    utc: bool = False
    embed: Optional[bool]

    class Config:
        orm_mode = True


class SwitchItem(FormItem):
    # Switch 开关
    type = FormItemEnum.switch
    option: Optional[str]
    trueValue: Optional[int]
    falseValue: Optional[int]
    value: Optional[bool]


class RichTextItem(FormItem):
    # 目前富文本编辑器基于两个库：froala 和 tinymce，默认使用 tinymce。
    type = FormItemEnum.input_rich_text
    body: Optional[Dict[str, Any]]
    options: Optional[Dict[str, Any]]
    receiver: Optional[str]
    videoReceiver: Optional[str]
    fileField: Optional[str]


class TextItem(FormItem):
    type = FormItemEnum.input_text
    body: Optional[Dict[str, Any]]
    trimContents: Optional[bool]  # 是否去除首尾空白文本。
    # resetValue: str = ""  # 清除后设置此配置项给定的值。


class TextareaItem(FormItem):
    # Textarea 多行文本输入框
    type = FormItemEnum.textarea
    body: Optional[Dict[str, Any]]
    minRows: Optional[int]  # 最小行数
    maxRows: Optional[int]  # 最大行数
    trimContents: Optional[bool]  # 是否去除首尾空白文本。


class TimeItem(FormItem):
    # Time 时间
    type = FormItemEnum.time
    body: Optional[Dict[str, Any]]
    value: Optional[datetime.time]  # 默认值
    timeFormat: str = "HH:mm:ss"  # 时间选择器值格式，更多格式类型请参考 moment
    format: str = "HH:mm:ss"  # = "X"  # 时间选择器值格式，更多格式类型请参考 moment
    inputFormat: str = "HH:mm:ss"  # 时间选择器显示格式，即时间戳格式，更多格式类型请参考 moment
    placeholder: Optional[str]  # 占位文本

    # timeConstrainst: Union[dict, bool]  # 请参考： react-datetime
    class Config:
        orm_mode = True


class UUIDItem(FormItem):
    # 随机生成一个 id，可以用于防止表单重复提交。
    type = FormItemEnum.uuid
    label = ""
    name: Optional[str]  # type: ignore
    length: Optional[int]


class CheckboxesItem(FormItem):
    """
    复选框
    """

    type = FormItemEnum.checkboxes
    optional: Optional[Union[List[Dict[str, str]]]]  # 选项组
    source: str  # 动态选项组
    delimeter: bool = False  # 拼接符
    labelField: str = "label"  # 选项标签字段
    valueField: str = "value"  # 选项值字符
    joinValues: bool = False  # 拼接值
    extractValue: bool = True  # 提取值
    columnsCount: int = 1  # 选项按几列显示，默认为一列
    checkAll: bool = False  # 是否支持全选
    defaultCheckAll: bool = False  # 默认是否全选


class DynaticCheckboxesItem(CheckboxesItem):
    """
    可变值复选框
    """

    creatable: bool = False  # 新增选项
    createBtnLabel: Optional[str]  # 新增选项
    addControls: Optional[List[str]]  # 自定义新增单项
    addApi: Optional[str]  # 配置新增选项接口
    editable: bool = False  # 编辑选项
    editControls: Optional[List[str]]  # 自定义编辑表单项
    editApi: Optional[str]  # 配置编辑选项接口
    removable: bool = False  # 删除选项
    deleteApi: Optional[str]  # 配置删除选项接口


class TransferItem(FormItem):
    # Transfer 穿梭器
    type = FormItemEnum.transfer
    options: Optional[List[Union[dict, str]]]  # 选项组
    source: Optional[str]  # 动态选项组
    delimeter: Optional[str]  # 拼接符
    joinValues: Optional[bool]  # 拼接值
    extractValue: Optional[bool]  # 提取值
    labelField: Optional[str]  # 选项标签字段
    valueField: Optional[str]  # 选项值字段
    searchable: bool = False  # 当设置为 true 时表示可以通过输入部分内容检索出选项。
    searchApi: Optional[str]  # 如果想通过接口检索，可以设置个 api。
    statistics: bool = True  # 是否显示统计数据
    selectTitle: Optional[str]  # 左侧的标题文字
    resultTitle: Optional[str]  # 右侧结果的标题文字
    sortable: bool = False  # 结果可以进行拖拽排序
    selectMode: str = "list"  # 可选：list、table、tree、chained、associated。分别为：列表形式、表格形式、树形选择形式、级联选择形式，关联选择形式（与级联选择的区别在于，级联是无限极，而关联只有一级，关联左边可以是个 tree）。
    searchResultMode: Optional[str]  # 如果不设置将采用 selectMode 的值，可以单独配置，参考 selectMode，决定搜索结果的展示形式。
    columns: Optional[List[dict]]  # 当展示形式为 table 可以用来配置展示哪些列，跟 table 中的 columns 配置相似，只是只有展示功能。
    leftOptions: Optional[List[dict]]  # 当展示形式为 associated 时用来配置左边的选项集。
    leftMode: Optional[str]  # 当展示形式为 associated 时用来配置左边的选择形式，支持 list 或者 tree。默认为 list。
    rightMode: Optional[str]  # 当展示形式为 associated 时用来配置右边的选择形式，可选：list、table、tree、chained。


# fixme 参考pickerSchema 需要补充值
class PickerSchema(BaseModel):
    model = "table"
    name: str
    # quickSaveApi: Optional[str]
    # quickSaveItemApi: Optional[str]
    # draggable: Optional[bool]
    # headerToolbar: Optional[Any]  # 配置搜索框用
    columns: Optional[List[Column]]


class PickerItem(FormItem):
    # 列表选取，在功能上和 Select 类似，但它能显示更复杂的信息。默认和 Select 很像，但请看后面的 pickerSchema 设置。
    type = FormItemEnum.picker
    options: Optional[List[Dict[str, str]]]  # 动态选项组
    source: Optional[str]
    multiple: bool = False
    delimeter: bool = False  # 拼接符
    labelField: Optional[str]  # 选项标签字段
    valueField: Optional[str]  # 选项值字符
    joinValues: bool = False  # 拼接值
    extractValue: bool = True  # 提取值
    autoFill: Optional[Dict[str, str]]  # 自动填充到某个位置
    modalMode: Optional[str]  # 配置弹出方式，默认为dialog，也可以配置drawer
    pickerSchema: Optional[PickerSchema]  # 即用 List 类型的渲染，来展示列表信息。更多配置参考 CRUD
    embed: Optional[bool]  # 是否使用内嵌模式


class FileItem(FormItem):
    type = FormItemEnum.input_file
    receiver: str
    asBase64: bool = True


class ImageItem(FormItem):
    type = FormItemEnum.input_image
    multiple: Optional[bool]  # 多选
    receiver: str


class Custom(Column):
    type: str = "custom"
    onMount: Optional[str]
    onUpdate: Optional[str]
    onUnmount: Optional[str]
    html: Optional[str]
    inline: Optional[bool]
    id: Optional[str]


class SubForm(FormItem):
    """
    InputSubForm 子表单
    https://aisuda.bce.baidu.com/amis/zh-CN/components/form/input-sub-form
    """

    type = "input-sub-form"
    multiple: Optional[bool]  # 是否为多选模式
    btnLabel: Optional[str]  # 按钮默认名称
    minLength: Optional[int]  # 限制最小个数。
    maxLength: Optional[int]  # 限制最大个数。
    draggable: Optional[bool]  # 是否可拖拽排序
    addable: Optional[bool]  # 是否可新增
    removable: Optional[bool]  # 是否可删除
    form: Form
    addButtonText: Optional[str]  # 自定义新增一项的文本
    showErrorMsg: Optional[bool]  # 是否在左下角显示报错信息


class InputTable(FormItem):
    """
    表格
    """

    type = "input-table"
    addable: Optional[bool]  # 是否可新增
    editable: Optional[bool]  # 是否可编辑
    removable: Optional[bool]  # 是否可删除
    showAddBtn: Optional[bool]  # 是否显示添加按钮
    addApi: Optional[str]
    updateApi: Optional[str]
    deleteApi: Optional[str]
    addBtnLabel: Optional[str]  # 增加按钮名称
    addBtnIcon: Optional[str]  # "plus"	增加按钮图标
    copyBtnLabel: Optional[str]  # 复制按钮文字
    copyBtnIcon: Optional[str]  # "copy"	复制按钮图标
    editBtnLabel: Optional[str]  # ""	编辑按钮名称
    editBtnIcon: Optional[str]  # "pencil"	编辑按钮图标
    deleteBtnLabel: Optional[str]  # ""	删除按钮名称
    deleteBtnIcon: Optional[str]  # "minus"	删除按钮图标
    confirmBtnLabel: Optional[str]  # ""	确认编辑按钮名称
    confirmBtnIcon: Optional[str]  # "check"	确认编辑按钮图标
    cancelBtnLabel: Optional[str]  # ""	取消编辑按钮名称
    cancelBtnIcon: Optional[str]  # "times"	取消编辑按钮图标
    needConfirm: Optional[bool]  # true	是否需要确认操作，，可用来控控制表格的操作交互
    canAccessSuperData: Optional[bool]  # false	是否可以访问父级数据，也就是表单中的同级数据，通常需要跟 strictMode 搭配使用
    strictMode: Optional[bool]  # true	为了性能，默认其他表单项项值变化不会让当前表格更新，有时候为了同步获取其他表单项字段，需要开启这个。
    columns: Optional[List[Column]]  # 列信息
