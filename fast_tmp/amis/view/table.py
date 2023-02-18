from typing import Any, List, Optional, Union

from pydantic import BaseModel

from fast_tmp.amis.base import SchemaNode, _Action
from fast_tmp.amis.view import BadgeSchema


class TableColumn(BaseModel):
    label: Optional[str]
    name: str
    width: Union[str, int]
    remark: Optional[str]
    fixed: Optional[str]  # left | right | none
    popOver: Optional[Any]
    copyable: Optional[Any]  # bool 或 {icon: string, content:string}


class Table(SchemaNode):
    type = "type"
    title: Optional[str]  # 标题
    source: Optional[str]  # ${items}  数据源, 绑定当前环境变量
    affixHeader: Optional[bool]  # true  是否固定表头
    columnsTogglable: Optional[bool]  # 展示列显示开关, 自动即：列数量大于或等于 5 个时自动开启
    placeholder: Optional[str]  # 或者 SchemaTpl  暂无数据  当没数据的时候的文字提示
    className: Optional[str]  # panel-default  外层 CSS 类名
    tableClassName: Optional[str]  # table-db table-striped  表格 CSS 类名
    headerClassName: Optional[str]  # Action.md-table-header  顶部外层 CSS 类名
    footerClassName: Optional[str]  # Action.md-table-footer  底部外层 CSS 类名
    toolbarClassName: Optional[str]  # Action.md-table-toolbar  工具栏 CSS 类名
    columns: List[TableColumn]  # <Column>   用来设置列信息
    combineNum: Optional[int]  # 自动合并单元格
    itemActions: Optional[_Action]  # <Action>   悬浮行操作按钮组
    itemCheckableOn: Optional[str]  # 配置当前行是否可勾选的条件，要用 表达式
    itemDraggableOn: Optional[str]  # 配置当前行是否可拖拽的条件，要用 表达式
    checkOnItemClick: Optional[bool]  # false  点击数据行是否可以勾选当前行
    rowClassName: Optional[str]  # 给行添加 CSS 类名
    rowClassNameExpr: Optional[str]  # 通过模板给行添加 CSS 类名
    prefixRow: Optional[Any]  # 顶部总结行
    affixRow: Optional[Any]  # 底部总结行
    itemBadge: Optional[BadgeSchema]  # 行角标配置
    autoFillHeight: Optional[bool]  # 丨 {height: number}   内容区域自适应高度
    resizable: Optional[bool]  # true  列宽度是否支持调整
    selectable: Optional[bool]  # false  支持勾选
    multiple: Optional[bool]  # false  勾选 icon 是否为多选样式checkbox， 默认为radio
