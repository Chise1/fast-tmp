import logging
import re
from abc import abstractmethod
from typing import Any, Coroutine, Dict, Iterable, List, Optional, Tuple

from starlette.requests import Request
from tortoise import ManyToManyFieldInstance, Model
from tortoise.queryset import QuerySet

from fast_tmp.amis.column import Column, ColumnInline, QuickEdit
from fast_tmp.amis.formitem import FormItem, FormItemEnum
from fast_tmp.amis.page import Page
from fast_tmp.amis.response import AmisStructError
from fast_tmp.exceptions import NotFoundError
from fast_tmp.responses import AdminRes, ListDataWithPage

logger = logging.getLogger(__file__)

field_description = re.compile(r"^([^();]+)(\(.+\))?(:.*?)?;?")


class AbstractAmisAdminDB:
    """
    admin访问model的数据库指令
    """

    name: str

    def list_queryset(self, queryset: QuerySet) -> QuerySet:  # 列表
        """
        主要考虑是否需要预加载
        """
        return queryset

    def prefetch(self) -> Optional[str]:  # 列表
        """
        过滤规则，用于页面查询和过滤用
        要求值必须为select（多对一）或prefetch（多对多）
        """
        return None

    async def get_value(self, request: Request, obj: Model) -> Any:
        """
        获取值
        """
        return getattr(obj, self.name)

    async def set_value(self, request: Request, obj: Model, value: Any) -> Optional[Coroutine]:
        """
        设置值
        """
        pass

    def validate(self, value: Any, is_create=False) -> Any:
        """
        对数据进行校验
        is_create: 当model为创建的时候，如果默认值是函数，则会传空过来，这个时候需要调用函数生成值。
        """
        return value

    def __init__(self, _field_name: str, **kwargs):
        if not _field_name:
            raise AmisStructError("field_name can not be none")
        self.name = _field_name


class AmisOrm:
    """
    orm和amis之间的数据转换
    """

    def orm_2_amis(self, value: Any) -> Any:
        """
        orm的值转成amis需要的值
        """
        if callable(value):
            return value()
        return value

    def amis_2_orm(self, value: Any) -> Any:
        return value


class AbstractControl:
    """
    用户自定义的column组件
    """

    @abstractmethod
    def get_column(self, request: Request) -> Column:
        """
        获取column模型
        """

    @abstractmethod
    def get_column_inline(self, request: Request) -> Column:
        """
        获取内联修改的column
        """

    @abstractmethod
    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        """
        获取内联修改的column
        """

    def need_codenames(self, request: Request) -> Tuple[str, ...]:
        """
        返回需要的权限，
        多对多和多对一对应的select控件提供添加按钮
        """
        return ()


class BaseControl(AbstractAmisAdminDB, AbstractControl, AmisOrm):
    """
    默认的将model字段转control的类
    """

    label: str
    description: Optional[str]
    placeholder: Optional[str]
    null = False
    default = None
    _control: FormItem = None  # type: ignore
    _column: Column = None  # type: ignore
    _column_inline: ColumnInline = None  # type: ignore
    _control_type: FormItemEnum = FormItemEnum.input_text
    _many = False  # 多对多字段标记，查询的时候默认跳过

    def get_column(self, request: Request) -> Column:
        if not self._column:
            self._column = Column(name=self.name, label=self.label)
        return self._column

    def get_formitem(self, request: Request, codenames: Iterable[str]) -> FormItem:
        """
        获取页面表单字段，由于某些字段可以支持其他页面的创建，所以这里需要权限功能
        另 column_inline不应支持权限功能
        """
        if not self._control:
            self._control = FormItem(
                type=self._control_type,
                name=self.name,
                label=self.label,
                description=self.description,
                placeholder=self.placeholder,
            )
            if not callable(self.default):
                if not self.null:
                    self._control.required = True
                if self.default is not None:
                    self._control.value = self.orm_2_amis(self.default)
        return self._control

    def options(self):
        return None

    def get_column_inline(self, request: Request) -> Column:
        if not self._column_inline:
            column = self.get_column(request)
            self._column_inline = ColumnInline(
                type=column.type,
                name=self.name,
                label=self.label,
                quickEdit=QuickEdit(type=self._control_type, saveImmediately=True),
            )
            options = self.options()
            if options:
                self._column_inline.quickEdit.options = options
                if self.null:
                    self._column_inline.quickEdit.clearable = True
        return self._column_inline

    async def set_value(self, request: Request, obj: Model, value: Any):
        value = self.validate(value, is_create=request.method == "POST")
        setattr(obj, self.name, value)

    async def get_value(self, request: Request, obj: Model) -> Any:
        return self.orm_2_amis(getattr(obj, self.name))

    def __init__(
        self,
        label: str,
        name: str,
        null: bool,
        default: Any,
        description: Optional[str] = None,
        placeholder: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self.name = name
        self.null = null
        self.default = default
        self.label = label
        self.description = description
        self.placeholder = placeholder


class BaseAdminControl(BaseControl):
    """
    ModelAdmin使用的类型
    """

    _field: Any
    _prefix: str = ""  # 需要赋值

    @property
    def field(self):
        if not self._field:
            raise AttributeError("prefix can not be none")
        return self._field

    @field.setter
    def field(self, field):
        self._field = field

    @property
    def prefix(self):
        if not self._prefix:
            raise AttributeError("prefix can not be none")
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix

    def __init__(
        self,
        label: str,
        name: str,
        null: bool,
        default: Any,
        description: Optional[str] = None,
        placeholder: Optional[str] = None,
        field: Any = None,
        prefix: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(label, name, null, default, description, placeholder, **kwargs)
        if field:
            if field.description:
                values = field_description.match(field.description)
                if values and not isinstance(
                    field, ManyToManyFieldInstance
                ):  # todo 还没想好多对多怎么处理 一对多也没想好怎么处理 枚举类型description默认有值，需要自己进行覆盖
                    label, description, placeholder = values.groups()
                    self.label = self.label or label or name
                    self.description = self.description or description
                    self.placeholder = self.placeholder or placeholder

            self.field = field
        self.prefix = prefix
        if not self.label:
            self.label = name

    def validate(self, value: Any, is_create=False) -> Any:
        if not value and is_create:
            if (
                callable(self.field.default) and not self.field.null
            ):  # 不为空且默认值是函数的时候，前段页面如果传null则使用默认值
                return self.field.default()
        value = self.amis_2_orm(value)
        self.field.validate(value)
        return value


class ModelFilter:
    name = ""
    type: Optional[str] = None
    label: Optional[str]
    _field: AmisOrm

    def filter_control(self, request) -> dict:
        ret = {
            "type": self.type,
            "label": self.label,
            "name": self.name,
        }
        ret.update(self.kwargs)
        return ret

    @abstractmethod
    def queryset(self, request: Request, queryset: QuerySet, val: Any) -> QuerySet:
        """
        拼接字段用
        """

    def __init__(
        self,
        name: str,
        field: Optional[AmisOrm] = None,
        type: str = "input-text",
        label: Optional[str] = None,
        **kwargs,
    ):
        self.name = name
        self._field = field or AmisOrm()
        self.type = type
        self.label = label or self.name
        self.kwargs = kwargs


class PageRouter:
    """
    页面基类，用于提供注册到admin管理页面的抽象类
    name: 导航栏名字
    prefix: 为接口的resource
    """

    _name: str
    _prefix: str

    @abstractmethod
    async def get_app_page(self, request: Request) -> Page:
        """
        继承该类并实现该接口,返回一个Page实例
        该接口会被fast_tmp.admin.endpoint里面的```/{resource}/schema```接口调用
        其中resource参数即为prefix
        """

    def __init__(self, prefix: str, name: str):
        """
        注册到admin的页面会生成对应页面权限，权限codename为{prefix}_create、{prefix}_update、{prefix}_delete、{prefix}_list

        name: 导航栏名字
        prefix: 为接口的resource
        """
        self._name = name
        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix

    @property
    def name(self) -> str:
        return self._name

    async def router(self, request: Request, resource: str, method: str) -> AdminRes:
        """
        用于自定义接口的方法
        当自定义该接口之后，会被fast_tmp.admin.endpoint里面的```/{resource}/extra/{prefix}```接口调用
        支持的method为["POST", "GET", "DELETE", "PUT", "PATCH"]
        """
        raise NotFoundError("not found function.")

    @abstractmethod
    def get_create_controls(
        self, request: Request, codenames: Iterable[str]
    ) -> Tuple[FormItem, ...]:
        """
        当外键或多对多创建的时候，子表的创建字段由此返回
        """

    @property
    def site(self):
        """
        左侧导航栏的显示配置
        """
        return {
            "label": self.name,
            "url": self.prefix,
            "schemaApi": self.prefix + "/schema",
            # "visible": False,  # 不显示在菜单中
        }


# 操作数据库的方法
class ModelSession:
    """
    后台管理页面数据库操作基类，包含后台页面对数据操作的所有需要的方法
    注意，不是所有接口都需要实现，针对自己的需求实现部分接口即可
    """

    @abstractmethod
    async def list(
        self,
        request: Request,
        perPage: int = 10,
        page: int = 1,
        orderBy: Optional[str] = None,
        orderDir: Optional[str] = None,
    ) -> ListDataWithPage:
        """
        获取数据列表
        """

    @abstractmethod
    async def patch(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        """
        对在表单上快速编辑的（inline类型）数据的进行修改
        """

    @abstractmethod
    async def create(self, request: Request, data: Dict[str, Any]) -> Model:
        """
        创建数据
        """

    @abstractmethod
    async def delete(self, request: Request, pk: str):
        """
        删除某条数据
        """

    @abstractmethod
    async def get_update(self, request: Request, pk: str) -> dict:
        """
        获取要更新的数据
        """

    @abstractmethod
    async def select_options(
        self,
        request: Request,
        name: str,
        pk: Optional[str],
        perPage: Optional[int],
        page: Optional[int],
    ) -> List[Dict[str, str]]:
        """
        多对多，多对一等情况下需要枚举选择的时候，返回数据列表
        返回数据结构大致如下：
        [{"label":"xxx","value":"xxx"}]
        value可以使数字或字符串
        """

    @abstractmethod
    async def update(self, request: Request, pk: str, data: Dict[str, Any]) -> Model:
        """
        更新数据
        """

    async def check_perm(self, request: Request, base_codename: str):
        """
        检测权限是否满足
        主要是被endpoint里面进行调用，create update,delete, list四个权限
        如果需要检测权限，需要这里进行修改
        示例：
        user = request.user
        if not await user.has_perm(codename.lower()):
            raise PermError()
        """
