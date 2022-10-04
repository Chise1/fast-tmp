from enum import Enum


class FormWidgetSize(
    str,
    Enum,
):
    full = "full"
    lg = "lg"  # 大
    md = "md"  # 中,默认值
    sm = "sm"  # 小
    xs = "xs"  # 极小


class ControlEnum(str, Enum):
    text = "text"
    textarea = "textarea"
    input_text = "input-text"
    switch = "switch"  # 开关
    select = "select"
    number = "input-number"
    native_number = "native-number"  # exploer natave number
    array = "array"
    date = "input-date"
    datetime = "input-datetime"
    uuid = "uuid"
    rich_text = "rich-text"
    time = "input-time"
    mapping = "mapping"
    transfer = "transfer"
    checkboxes = "checkboxes"
    picker = "picker"
    custom = "custom"
    input_password = "input-password"
    input_image = "input-image"
    input_file = "input-file"


class ItemModel(str, Enum):
    horizontal = "horizontal"
    inline = "inline"
    normal = "normal"


class WidgetSize:
    lg = "lg"  # 大
    md = "md"  # 中,默认值
    sm = "sm"  # 小
    xs = "xs"  # 极小


class ValidateEnum(str, Enum):
    isEmptyString = "isEmptyString"  # 必须是空白字符。注意！ 该格式校验是值，校验空白字符，而不是当前表单项是否为空，想校验是否为空，请配置
    isEmail = "isEmail"  # 必须是Email。
    isUrl = "isUrl"  # 必须是Url。
    isNumeric = "isNumeric"  # 必须是数值。
    isAlpha = "isAlpha"  # 必须是字母。
    isAlphanumeric = "isAlphanumeric"  # 必须是字母或者数字。
    isInt = "isInt"  # 必须是整形。
    isFloat = "isFloat"  # 必须是浮点形。
    isLength = "isLength"  #: length 是否长度正好等于设定值。
    minLength = "minLength"  #: length 最小长度。
    maxLength = "maxLength"  #: length最大长度。
    maximum = "maximum"  # number    最大值。
    minimum = "minimum"  # number    最小值。
    equals = "equals"  #: xxx    当前值必须完全等于    xxx。
    equalsField = "equalsField"  #: xxx    当前值必须与    xxx    变量值一致。
    isJson = "isJson"  # 是否是合法的Json字符串。
    notEmptyString = "notEmptyString"  # 要求输入内容不是空白。
    isUrlPath = "isUrlPath"  # 是    url    路径。
    matchRegexp = "matchRegexp"  #: / foo / 必须命中某个正则。
    matchRegexp1 = "matchRegexp1"  #: / foo / 必须命中某个正则。
    matchRegexp2 = "matchRegexp2"  #: / foo / 必须命中某个正则。
    matchRegexp3 = "matchRegexp3"  #: / foo / 必须命中某个正则。
    matchRegexp4 = "matchRegexp4"  #: / foo / 必须命中某个正则。
