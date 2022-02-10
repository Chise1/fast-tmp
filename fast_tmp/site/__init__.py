from typing import Any, Dict, List, Optional, Tuple, Type

from sqlalchemy import Column, select
from sqlalchemy.orm import MANYTOMANY, MANYTOONE, ONETOMANY, RelationshipProperty

from fast_tmp.admin.schema.actions import AjaxAction, DialogAction
from fast_tmp.admin.schema.buttons import Operation
from fast_tmp.admin.schema.crud import CRUD
from fast_tmp.admin.schema.enums import ButtonLevelEnum
from fast_tmp.admin.schema.forms import Form
from fast_tmp.admin.schema.frame import Dialog
from fast_tmp.admin.schema.page import Page

from ..admin.constant import crud_root_rooter
from .utils import get_pk, get_real_column_field, make_columns, make_controls


class ModelAdmin:
    model: Any  # model
    __name: Optional[str] = None
    # list
    list_display: Tuple[Column, ...] = ()
    # list_display_links: Tuple[Column, ...] = ()
    list_per_page: int = 10
    list_max_show_all: int = 200
    # search list
    search_fields: Tuple[Column, ...] = ()
    filter_fields: Tuple[Column, ...] = ()
    # create
    create_fields: Tuple[Column, ...] = ()
    # exclude: Tuple[Union[str, BaseModel], ...] = ()
    # update ,如果为空则取create_fields
    update_fields: Tuple[Column, ...] = ()

    methods: Tuple[str, ...] = ("list", "retrieve", "create", "put", "delete", "deleteMany")
    # actions_func: Dict[
    #     str, Callable
    # ] = (
    #     {}
    # )  # 请求对应的调用函数，"list","retrieve","create","put","delete","deleteMany"有默认自定义方法，这里如果填了就是覆盖默认方法
    # 页面相关的东西
    __create_dialog: Any = None
    __get_pks: Any = None
    # page_model: Type[BaseModel]

    # prefix: str = "/admin"

    @classmethod
    def name(cls):
        if cls.__name is None:
            cls.__name = cls.model.__name__
        return cls.__name

    @classmethod
    def get_create_dialogation_button(cls):
        if cls.__create_dialog is None:
            cls.__create_dialog = DialogAction(
                label="新增",
                dialog=Dialog(
                    title="新增",
                    body=Form(
                        name=f"新增{cls.name()}",
                        title=f"新增{cls.name()}",
                        body=make_controls(cls.create_fields),
                        api=f"post:{crud_root_rooter}{cls.name()}/create",
                    ),
                ),
            )
        return cls.__create_dialog

    @classmethod
    def get_list_page(cls):
        return make_columns(cls.list_display)

    @classmethod
    def pks(cls):
        if cls.__get_pks is None:
            primary_keys = get_pk(cls.model).keys()
            del_path = []
            for pk in primary_keys:
                del_path.append(f"{pk}=${pk}")
            cls.__get_pks = "".join(del_path)
        return cls.__get_pks

    @classmethod
    def get_del_one_button(cls):
        return AjaxAction(
            label="删除",
            type="button",
            level=ButtonLevelEnum.danger,
            confirmText="确认要删除？",
            api="delete:" + crud_root_rooter + cls.name() + "/delete?" + cls.pks(),
        )

    @classmethod
    def get_update_one_button(cls):
        return DialogAction(
            label="修改",
            dialog=Dialog(
                title="修改",
                body=Form(
                    name=f"修改{cls.name()}",
                    body=make_controls(cls.update_fields),
                    api="put:" + crud_root_rooter + cls.name() + "/update?" + cls.pks(),
                    initApi="get:" + crud_root_rooter + cls.name() + "/update?" + cls.pks(),
                ),
            ),
        )

    @classmethod
    def get_operation(cls):
        buttons = []
        if "delete" in cls.methods:
            buttons.append(cls.get_del_one_button())
        if "update" in cls.methods and cls.update_fields:
            buttons.append(cls.get_update_one_button())
        return Operation(buttons=buttons)

    @classmethod
    def get_crud(cls):
        body = []
        if "create" in cls.methods and cls.create_fields:
            body.append(cls.get_create_dialogation_button())
        if "list" in cls.methods and cls.list_display:
            columns = []
            columns.extend(cls.get_list_page())
            columns.append(cls.get_operation())
            body.append(
                CRUD(
                    api=crud_root_rooter + cls.name() + "/list",
                    columns=columns,
                )
            )
        return body

    @classmethod
    def get_app_page(cls):
        return Page(title=cls.name(), body=cls.get_crud()).dict(exclude_none=True)

    @classmethod
    def create_model(cls, data: dict):
        """
        写入数据库之前调用
        """
        instance = cls.model()
        for k, v in data.items():
            field = getattr(cls.model, k)
            if isinstance(field.property, RelationshipProperty):
                if field.property.direction == MANYTOMANY:
                    model = field.mapper.class_
                    pk = list(get_pk(model).keys())[0]
                    for i in v:
                        child = model()
                        setattr(child, pk, i)
                        getattr(instance, k).append(child)
                elif field.property.direction == MANYTOONE:
                    field = get_real_column_field(field)
                    setattr(instance, field.key, v)
                elif field.property.direction == ONETOMANY:  # todo 暂时不考虑支持
                    # onetoone
                    if not getattr(field.property, "uselist"):
                        pass
                    else:
                        pass
                else:
                    raise AttributeError(
                        f"error relationshipfield: {cls.model}'s {field} relationship is not true."
                    )
            else:
                setattr(instance, k, v)
        return instance

    @classmethod
    def update_model(cls, instance: Any, data: dict) -> Any:
        """
        更新数据之前调用
        """
        for k, v in data.items():
            field = getattr(cls.model, k)
            if isinstance(field.property, RelationshipProperty):
                if field.property.direction == MANYTOMANY:
                    model = field.mapper.class_
                    pk = list(get_pk(model).keys())[0]
                    for i in v:
                        child = model()
                        setattr(child, pk, i)
                        getattr(instance, k).append(child)
                elif field.property.direction == MANYTOONE:
                    field = get_real_column_field(field)
                    setattr(instance, field.key, v)
                elif field.property.direction == ONETOMANY:  # todo 暂时不考虑支持
                    # onetoone
                    if not getattr(field.property, "uselist"):
                        pass
                    else:
                        pass
                else:
                    raise AttributeError(
                        f"error relationshipfield: {cls.model}'s {field} relationship is not true."
                    )
            else:
                setattr(instance, k, v)
        return instance

    @classmethod
    def get_clean_fields(cls, fields):
        """
        获取对外键进行处理过的列表,该方法主要用于数据处理
        """
        res = []
        for i in fields:
            if hasattr(i.property, "direction"):
                if i.property.direction in (MANYTOMANY, ONETOMANY):
                    continue
                if i.property.direction == MANYTOONE:
                    res.append(get_real_column_field(i))
            else:
                res.append(i)
        return res

    __list_sql = None

    @classmethod
    def get_list_sql(cls):
        if cls.__list_sql is None:
            __list_display = []
            for i in cls.list_display:
                if hasattr(i.property, "direction"):
                    if i.property.direction in (MANYTOMANY, ONETOMANY):
                        continue
                    if i.property.direction == MANYTOONE:
                        __list_display.append(get_real_column_field(i))
                else:
                    __list_display.append(i)
            cls.__list_sql = select(__list_display)
        return cls.__list_sql

    __one_sql = None

    @classmethod
    def get_one_sql(cls, pks: list):
        if cls.__one_sql is None:
            __list_display = cls.get_clean_fields(cls.update_fields)
            cls.__one_sql = select(__list_display)
        return cls.__one_sql.where(*pks)


model_list: Dict[str, List[Type[ModelAdmin]]] = {}


def register_model_site(model_group: Dict[str, List[Type[ModelAdmin]]]):
    model_list.update(model_group)


def get_model_site(resource: str) -> Optional[Type[ModelAdmin]]:
    for m_l in model_list.values():
        for i in m_l:
            if i.name() == resource:
                return i
    return None
