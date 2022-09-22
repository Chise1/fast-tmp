import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import HttpUrl
from pydantic.main import BaseModel

# from fast_tmp.amis.abstract_schema import Action
from fast_tmp.amis.forms import Control, SelectOption  # , Limit
from fast_tmp.amis.forms.enums import ControlEnum


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


class NumberItem(Control):
    type: ControlEnum = ControlEnum.number
    min: Optional[int]
    max: Optional[int]
    precision: Optional[int]  # 小数点后几位
    step: Optional[int]  # 选择的步长
    value: Optional[int]
    showSteps: Optional[bool] = False


class NativeNumber(Control):
    type: ControlEnum = ControlEnum.native_number


class SelectItem(Control):
    type: ControlEnum = ControlEnum.select
    clearable: Optional[bool]
    options: Optional[List[Union[SelectOption, str, int]]]
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
    addApi: Optional[HttpUrl]  # 配置增加接口，如果为空则不会保存
    editable: bool = False  # 前端是否可编辑
    editControls: Tuple[AddControl, ...] = (
        AddControl(type="text", name="label", label="选项标题"),
        AddControl(type="text", name="value", label="选项值"),
    )  # 配置修改值的弹框信息
    editApi: Optional[HttpUrl]
    deleteApi: Optional[HttpUrl]  # 配置删除接口


class ArrayItem(Control):
    type: ControlEnum = ControlEnum.array
    items: str = "text"  # 这个到时候改为枚举
    addable: bool = True  # 是否可新增
    removable: bool = True  # 是否可删除
    draggable: bool = False  # 是否可拖动排序，是否可以拖动排序, 需要注意的是当启用拖动排序的时候，
    # 会多一个$id 字段，具体请参考：https://baidu.gitee.io/amis/docs/components/form/array
    draggableTip: Optional[str]
    addButtonText: Optional[str]  # 新增按钮的文字
    minLength: Optional[int]  # 最短长度
    maxLength: Optional[int]  # 最长长度


class DatetimeItem(Control):
    type: ControlEnum = ControlEnum.datetime
    value: Optional[str]
    format: str = "YYYY-MM-DD HH:mm:ss"  # 'X'为时间戳格式,参考文档：
    # https://baidu.gitee.io/amis/zh-CN/docs/components/form/datetime
    inputFormat: str = "YYYY-MM-DD HH:mm:ss"  # 'X'为时间戳格式
    # shortcuts: List[str] = []  # "yesterday" ,"today", "tomorrow",now,{n}hoursago : n 小时前，例
    # 如：1daysago，下面用法相同,{n}hourslater : n 小时前，例如：1daysago
    utc: Optional[bool]
    clearable: Optional[bool]
    embed: Optional[bool]

    # timeConstrainst: bool = True  # 不知道干吗用的

    class Config:
        orm_mode = True


class DateItem(Control):
    type = ControlEnum.date
    value: Optional[str]
    format: str = "YYYY-MM-DD"  # 格式请参考文档：https://baidu.gitee.io/amis/zh-CN/docs/components/form/date  # 'X'为时间戳格式
    inputFormat: str = "YYYY-MM-DD"  # 'X'为时间戳格式
    # shortcuts: List[str] = []  # "yesterday" ,"today", "tomorrow"
    utc: bool = False
    clearable: bool = True
    embed: Optional[bool]
    # timeConstrainst: bool = True  # 不知道干吗用的

    class Config:
        orm_mode = True


class SwitchItem(Control):
    # Switch 开关
    type = ControlEnum.switch
    option: Optional[str]
    trueValue: Optional[int]
    falseValue: Optional[int]
    value: Optional[bool]


class RichTextItem(Control):
    # 目前富文本编辑器基于两个库：froala 和 tinymce，默认使用 tinymce。
    type = ControlEnum.rich_text
    body: Optional[Dict[str, Any]]


class TextItem(Control):
    type = ControlEnum.input_text
    body: Optional[Dict[str, Any]]
    trimContents: Optional[bool]  # 是否去除首尾空白文本。
    # clearable: Optional[bool]  # 是否可清除
    # resetValue: str = ""  # 清除后设置此配置项给定的值。


class TextareaItem(Control):
    # Textarea 多行文本输入框
    type = ControlEnum.textarea
    body: Optional[Dict[str, Any]]
    minRows: Optional[int]  # 最小行数
    maxRows: Optional[int]  # 最大行数
    trimContents: Optional[bool]  # 是否去除首尾空白文本。


class TimeItem(Control):
    # Time 时间
    type = ControlEnum.time
    body: Optional[Dict[str, Any]]
    value: Optional[datetime.time]  # 默认值
    timeFormat: str = "HH:mm"  # 时间选择器值格式，更多格式类型请参考 moment
    format: str = "X"  # 时间选择器值格式，更多格式类型请参考 moment
    inputFormat: str = "HH:mm"  # 时间选择器显示格式，即时间戳格式，更多格式类型请参考 moment
    placeholder: Optional[str]  # 占位文本
    clearable: bool = True  # 是否可清除
    timeConstrainst: Union[dict, bool]  # 请参考： react-datetime


class UUIDItem(Control):
    # 随机生成一个 id，可以用于防止表单重复提交。
    type = ControlEnum.uuid
    name: Optional[str]  # type: ignore
    length: Optional[int]


class CheckboxesItem(Control):
    """
    复选框
    """

    type = ControlEnum.checkboxes
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
    addApi: Optional[HttpUrl]  # 配置新增选项接口
    editable: bool = False  # 编辑选项
    editControls: Optional[List[str]]  # 自定义编辑表单项
    editApi: Optional[HttpUrl]  # 配置编辑选项接口
    removable: bool = False  # 删除选项
    deleteApi: Optional[HttpUrl]  # 配置删除选项接口


class TransferItem(Control):
    # Transfer 穿梭器
    type = ControlEnum.transfer
    options: Optional[List[Union[dict, str]]]  # 选项组
    source: Optional[str]  # 动态选项组#fixme:路由替换需要支持source
    delimeter: Optional[str]  # 拼接符
    joinValues: Optional[bool]  # 拼接值
    extractValue: Optional[bool]  # 提取值
    labelField: Optional[str]  # 选项标签字段
    valueField: Optional[str]  # 选项值字段
    searchable: bool = False  # 当设置为 true 时表示可以通过输入部分内容检索出选项。
    searchApi: Optional[HttpUrl]  # 如果想通过接口检索，可以设置个 api。
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


class PickerItem(Control):
    # 列表选取，在功能上和 Select 类似，但它能显示更复杂的信息。默认和 Select 很像，但请看后面的 pickerSchema 设置。
    type = ControlEnum.picker
    options: Optional[List[Dict[str, str]]]  # 动态选项组
    source: Optional[str]
    multiple: bool = False
    delimeter: bool = False  # 拼接符
    labelField: str = "label"  # 选项标签字段
    valueField: str = "value"  # 选项值字符
    joinValues: bool = False  # 拼接值
    extractValue: bool = True  # 提取值
    autoFill: Optional[Dict[str, str]]  # 自动填充到某个位置
    modalMode: Optional[str]  # 配置弹出方式，默认为dialog，也可以配置drawer
    pickerSchema: Optional[Dict]  # 即用 List 类型的渲染，来展示列表信息。更多配置参考 CRUD
    embed: Optional[bool]  # 是否使用内嵌模式


# class ButtonToolbarItem(Control):
#     """
#     按钮组
#     """
#
#     type = "button-toolbar"
#     label: str = "按钮组"
#     buttons: List[_Action]
#
#
# class ChainSelectItem(Control):
#     # 链式下拉框
#     pass
#
#
# class CheckboxItem(Control):
#     # 勾选框
#     type = "checkbox"
#     option: Optional[str]  # 选项说明
#     trueValue: bool = True
#     falseValue: bool = False
#
#

#
# class CityItem(Control):
#     # 城市选择器
#     pass
#
#
# class ColorItem(Control):
#     # 颜色选择器
#     pass
#
#
# class ComboControlItem(Control):
#     # Combo组合中的表单项
#     type = "combo-control"
#     columnClassName: Optional[str]  # 列的类名，可以用它配置列宽度。默认平均分配。
#     unique: Optional[bool]  # 设置当前列值是否唯一，即不允许重复选择。
#
#
# class ComboItem(Control):
#     # Combo组合
#     type = "form"
#     debug: bool = True
#     api: Optional[HttpUrl]  #
#     mode: Optional[str]
#     multiLine: bool = False  # 是否分多行展示
#     multiple: bool = False  # 是否实现多选模式
#     minLength: Optional[int]  # 多选模式下配置Combo可添加的最少条数
#     maxLength: Optional[int]  # 多选模式下配置Combo可添加的最大条数
#     flat: bool = False  # 默认多选模式下，数据格式是对象数组的形式，当你配置的组合中只有一个表单项时，可以配置"flat": true，将值进行打平处理。
#     formClassName: Optional[str]  # 单组表单项的类名
#     controls: Optional[List[ComboControlItem]]  # 组合展示的表单项
#     joinValues: bool = True  # 默认为 true 当扁平化开启的时候，是否用分隔符的形式发送给后端，否则采用 array 的方式。
#     delimiter: str = "false"  # 当扁平化开启并且 joinValues 为 true 时，用什么分隔符。
#     addable: bool = False  # 是否可新增
#     removable: bool = False  # 是否可删除
#     deleteApi: Optional[HttpUrl]  # 如果配置了，则删除前会发送一个 api，请求成功才完成删除
#     deleteConfirmText: str = "确认要删除？"  # 当配置 deleteApi 才生效！删除时用来做用户确认
#     draggable: bool = False  # 是否可以拖动排序, 需要注意的是当启用拖动排序的时候，会多一个$id 字段
#     draggableTip: str = "可通过拖动每行中的【交换】按钮进行顺序调整"  # 可拖拽的提示文字
#     addButtonText: str = "新增"  # 新增按钮文字
#     scaffold: dict = {}  # 单组表单项初始值
#     canAccessSuperData: bool = False  # 指定是否可以自动获取上层的数据并映射到表单项上
#     conditions: Optional[dict]  # 数组的形式包含所有条件的渲染类型，单个数组内的test 为判断条件，数组内的controls为符合该条件后渲染的schema
#     typeSwitchable: bool = False  # 是否可切换条件，配合conditions使用
#     noBorder: bool = False  # 单组表单项是否显示边框
#     strictMode: bool = True  # 默认为严格模式，设置为 false 时，当其他表单项更新是，里面的表单项也可以及时获取，否则不会。
#     syncFields: Optional[str]  # 配置同步字段。只有 strictMode 为 false 时有效。如果 combo 层级比较深，
#     # 底层的获取外层的数据可能不同步。但是给 combo 配置这个属性就能同步下来。输入格式：["os"]
#
#
# class DiffEditorItem(Control):
#     # 对比编辑器
#     pass
#
#
# class EditorItem(Control):
#     # 代码编辑器
#     pass
#
#
# class FieldSetItem(Control):
#     # 表单项集合
#     type = "form"
#     api: Optional[HttpUrl]
#     className: Optional[str]  # CSS 类名
#     headingClassName: Optional[str]  # 标题 CSS 类名
#     bodyClassName: Optional[str]  # 内容区域 CSS 类名
#
#
# class FileItem(Control):
#     # 文件上传
#     type = "form"
#     reciever: Optional[HttpUrl]  # 上传文件接口
#     accept: str = "text/plain"  # 默认只支持纯文本，要支持其他类型，请配置此属性为文件后缀.xxx
#     asBase64: bool = False  # 将文件以base64的形式，赋值给当前组件
#     asBlob: bool = False  # 将文件以二进制的形式，赋值给当前组件
#     maxSize: Optional[int]  # 默认没有限制，当设置后，文件大小大于此值将不允许上传。单位为KB
#     maxLength: Optional[int]  # 默认没有限制，当设置后，一次只允许上传指定数量文件。
#     multiple: bool = False  # 是否多选。
#     joinValues: bool = True  # 拼接值
#     extractValue: bool = False  # 提取值
#     delimiter: str = ","  # 拼接符
#     autoUpload: bool = True  # 否选择完就自动开始上传
#     hideUploadButton: bool = False  # 隐藏上传按钮
#     stateTextMap: dict = {
#         "init": "",
#         "pending": "等待上传",
#         "uploading": "上传中",
#         "error": "上传出错",
#         "uploaded": "已上传",
#         "ready": "",
#     }  # 上传状态文案
#     fileField: str = "file"  # 如果你不想自己存储，则可以忽略此属性。
#     downloadUrl: Union[
#         str, bool
#     ] = ""  # 默认显示文件路径的时候会支持直接下载，可以支持加前缀如：http://xx.dom/filename= ，如果不希望这样，可以把当前配置项设置为 false。
#     useChunk: Union[
#         str, bool
#     ] = "auto"  # amis 所在服务器，限制了文件上传大小不得超出 10M，所以 amis 在用户选择大文件的时候，自动会改成分块上传模式。
#     chunkSize: int = 5 * 1024 * 1024  # 分块大小
#     startChunkApi: Optional[HttpUrl]  # startChunkApi
#     chunkApi: Optional[HttpUrl]  # chunkApi
#     finishChunkApi: Optional[HttpUrl]  # finishChunkApi
#
#
# class FormulaItem(Control):
#     # Formula公式
#     pass
#
#
# class GroupItem(Control):
#     # Group表单项组
#     pass
#
#
# class HBoxItem(Control):
#     # HBox
#     pass
#
#
# class HiddenItem(Control):
#     # Hidden隐藏字段
#     pass
#
#
# class ImageItem(Control):
#     # Image图片
#     type = "image"
#     reciever: Optional[HttpUrl]  # 上传文件接口
#     accept: str = ".jpeg,.jpg,.png,.gif"  # 支持的图片类型格式，请配置此属性为图片后缀，例如.jpg,.png
#     maxSize: Optional[int]  # 默认没有限制，当设置后，文件大小大于此值将不允许上传。单位为B
#     maxLength: Optional[int]  # 默认没有限制，当设置后，一次只允许上传指定数量文件。
#     multiple: bool = False  # 是否多选。
#     joinValues: bool = True  # 拼接值
#     extractValue: bool = False  # 提取值
#     delimiter: str = ","  # 拼接符
#     autoUpload: bool = True  # 否选择完就自动开始上传
#     hideUploadButton: bool = False  # 隐藏上传按钮
#     fileField: str = "file"  # 如果你不想自己存储，则可以忽略此属性。
#     crop: Union[bool, dict]  # 用来设置是否支持裁剪。
#     # limit:Optional[Limit] # 限制图片大小，超出不让上传。
#
#
# class InputGroupItem(Control):
#     # 输入框组合
#     pass
#
#
# class ListSchemaItem(Control):
#     # 列表一般用来实现选择，可以单选也可以多选，和 Radio/Checkboxs 最大的不同是在展现方面支持带图片。
#     type = "list"
#     clearable: bool = True
#     options: Union[List[dict], List[str]]
#     source: Union[HttpUrl, str]
#     multiple: bool = False
#     labelField: str = "label"
#     valueField: str = "value"
#     joinValues: bool = True
#     extractValue: bool = False
#     autoFill: Optional[dict]
#
#

#
#
# class MatrixItem(Control):
#     # 矩阵类型的输入框。
#     type = "page"
#
#
# class NestedSelectItem(Control):
#     # NestedSelect 级联选择器
#     type = "page"
#     body: Optional[dict]
#
#
# class PanelItem(Control):
#     # 展现上将多个 表单项 放同一个容器下。
#     type = "page"
#
#

#
#
# class RadiosItem(Control):
#     # 用于实现单选。
#     type = "page"
#     body: Optional[Dict[str, Any]]
#     options: Union[List[str], List[dict]]  # 选项组
#     source: Union[str, HttpUrl]  # 动态选项组
#     labelField: str = "label"  # 选项标签字段
#     valueField: str = "value"  # 选项值字段
#     columnsCount: int = 1  # 选项按几列显示，默认为一列
#     autoFill: Optional[dict]  # 自动填充
#
#
# class RatingItem(Control):
#     # Rating 评分
#     type = "page"
#
#
# class RangeItem(Control):
#     # Range 滑块,可以用于选择单个数值或数值范围。
#     type = "page"
#     body: Optional[Dict[str, Any]]
#
#
# class RepeatItem(Control):
#     # Repeat 重复频率选择器
#     type = "page"
#     body: Optional[Dict[str, Any]]
#
#

#
#
# class ServiceItem(Control):
#     # Service 功能容器
#     type = "page"
#     body: Optional[Dict[str, Any]]
#
#
# class SubFormItem(Control):
#     # SubForm 子表单
#     type = "page"
#     body: Optional[Dict[str, Any]]
#
#

#
#
# class StaticItem(Control):
#     # Static 静态展示   用来在表单中，展示静态数据
#     type = "page"
#     body: Optional[Dict[str, Any]]
#
#
# class TabsItem(Control):
#     # Tabs 选项卡   有多组输入框时，也可以通过选项卡来分组。
#     type = "page"
#     body: Optional[Dict[str, Any]]
#
#
# class TableItem(Control):
#     # Table 表格
#     type = "table"
#     body: Optional[Dict[str, Any]]
#     addable: bool = False  # 是否可增加一行
#     editable: bool = False  # 是否可编辑
#     removable: bool = False  # 是否可删除
#     showAddBtn: bool = True  # 是否显示添加按钮
#     addApi: Optional[HttpUrl]  # 新增时提交的 API
#     updateApi: Optional[HttpUrl]  # 修改时提交的 API
#     deleteApi: Optional[HttpUrl]  # 删除时提交的 API
#     addBtnLabel: Optional[str]  # 增加按钮名称
#     addBtnIcon: str = "fa fa-plus"  # 增加按钮图标
#     updateBtnLabel: str = ""  # 更新按钮名称
#     updateBtnIcon: str = "fa fa-pencil"  # 更新按钮图标
#     deleteBtnLabel: str = ""  # 删除按钮名称
#     deleteBtnIcon: str = "fa fa-minus"  # 删除按钮图标
#     confirmBtnLabel: str = ""  # 确认编辑按钮名称
#     confirmBtnIcon: str = "fa fa-check"  # 确认编辑按钮图标
#     cancelBtnLabel: str = ""  # 取消编辑按钮名称
#     cancelBtnIcon: str = "fa fa-times"  # 取消编辑按钮图标
#     needConfirm: bool = True  # 是否需要确认操作，，可用来控控制表格的操作交互
#     canAccessSuperData: bool = False  # 是否可以访问父级数据，也就是表单中的同级数据，通常需要跟 strictMode 搭配使用
#     strictMode: bool = True  # 为了性能，默认其他表单项项值变化不会让当前表格更新，有时候为了同步获取其他表单项字段，需要开启这个。
#     columns: Optional[List[Dict[str, bool]]]  # 列信息
#
#
# # class TagItem(AbstractControl):
# #     # Tag 标签选择器
# #     type = "page"
# #     body: Optional[Dict[str, Any]]
# #     options: List[Union[dict, str]]  # 选项组
# #     optionsTip: List[Union[dict, str]] = ["最近您使用的标签"]   # 选项提示
# #     source: str  # 动态选项组
# #     delimeter: str = 'false'  # 拼接符
# #     labelField: str = "label"    # 选项标签字段
# #     valueField: str = "value"    # 选项值字符
# #     joinValues: bool = True  # 拼接值
# #     extractValue: bool = False   # 提取值
# #     clearable: bool = False  # 在有值的时候是否显示一个删除图标在右侧。
# #     resetValue: str = ""  # 删除后设置此配置项给定的值。
#
#

#
#

#
#

#

#
# class TabsTransferItem(Control):
#     # TabsTransfer 组合穿梭器
#     pass
#
#
# class TreeItem(Control):
#     # Tree 树形选择框
#     type = "page"
#     body: Optional[Dict[str, Any]]
#     options: List[Union[dict, str]]  # 选项组
#     source: Union[str, HttpUrl]  # 动态选项组
#     autoComplete: bool = True  # 是否对选项启动自动补全
#     multiple: bool = False  # 是否多选
#     delimeter: Optional[str]  # 拼接符
#     labelField: str = "label"  # 选项标签字段
#     valueField: str = "value"  # 选项值字段
#     joinValues: bool = True  # 拼接值
#     extractValue: bool = False  # 提取值
#     creatable: bool = False  # 新增选项
#     addControls: Optional[List]  # 自定义新增表单项
#     addApi: Optional[HttpUrl]  # 配置新增选项接口
#     editable: bool = False  # 编辑选项
#     editControls: Optional[List]  # 自定义编辑表单项
#     editApi: Optional[HttpUrl]  # 配置编辑选项接口
#     removable: bool = False  # 删除选项
#     deleteApi: Optional[HttpUrl]  # 配置删除选项接口
#     searchable: bool = False  # 是否可检索，仅在 type 为 tree-select 的时候生效
#     hideRoot: bool = True  # 如果想要显示个顶级节点，请设置为 false
#     rootLabel: Union[bool, str] = "顶级"  # 当 hideRoot 不为 false 时有用，用来设置顶级节点的文字。
#     showIcon: bool = True  # 是否显示图标
#     showRadio: bool = False  # 是否显示单选按钮，multiple 为 false 是有效。
#     initiallyOpen: bool = True  # 设置是否默认展开所有层级。
#     unfoldedLevel: int = 0  # 设置默认展开的级数，只有initiallyOpen不是true时生效。
#     cascade: bool = False  # 当选中父节点时不自动选择子节点。
#     withChildren: bool = False  # 选中父节点时，值里面将包含子节点的值，否则只会保留父节点的值。
#     onlyChildren: bool = False  # 多选时，选中父节点时，是否只将其子节点加入到值中。
#     rootCreatable: bool = False  # 是否可以创建顶级节点
#     rootCreateTip: str = "添加一级节点"  # 创建顶级节点的悬浮提示
#     minLength: Optional[int]  # 最少选中的节点数
#     maxLength: Optional[int]  # 最多选中的节点数
#
#
# class TreeSelectItem(AbstractControl):
#     # TreeSelect 树形选择器
#     type = "page"
#     body: Optional[Dict[str, Any]]
#
# # fixme:type有问题
# # class YearItem(Control):
# #     # Year年
# #     type = "page"
# #     body: Optional[Dict[str, Any]]
