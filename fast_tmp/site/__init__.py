from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel
from sqlalchemy import Column

from fast_tmp.admin.schema.actions import AjaxAction, DialogAction
from fast_tmp.admin.schema.buttons import Operation
from fast_tmp.admin.schema.crud import CRUD
from fast_tmp.admin.schema.enums import ButtonLevelEnum
from fast_tmp.admin.schema.forms import Form
from fast_tmp.admin.schema.frame import Dialog
from fast_tmp.admin.schema.page import Page

from ..admin.constant import crud_root_rooter
from .utils import get_columns_from_model, get_controls_from_model, get_pk


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
    page_model: Type[BaseModel]
    prefix: str = "/admin"

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
                        body=get_controls_from_model(cls.create_fields),
                        api=f"post:{crud_root_rooter}{cls.name()}/create",
                    ),
                ),
            )
        return cls.__create_dialog

    @classmethod
    def get_list_page(cls):
        return get_columns_from_model(cls.list_display)

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
                    body=get_controls_from_model(cls.update_fields),
                    api="put:" + crud_root_rooter + cls.name() + "/update?" + cls.pks(),
                    initApi="get:" + crud_root_rooter + cls.name() + "/update?" + cls.pks(),
                ),
            ),
        )

    @classmethod
    def get_operation(cls):
        primary_keys = get_pk(cls.model).keys()
        del_path = []
        for pk in primary_keys:
            del_path.append(f"{pk}=${pk}")
        return Operation(buttons=[cls.get_del_one_button(), cls.get_update_one_button()])

    @classmethod
    def get_crud(cls):
        body = []
        body.append(cls.get_create_dialogation_button())
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
        return cls.model(**data)

    @classmethod
    def update_model(cls, model: Any, data: dict) -> Any:
        """
        更新数据之前调用
        """
        for k, v in data.items():
            setattr(model, k, v)
        return model


model_list: Dict[str, List[Type[ModelAdmin]]] = {}


def register_model_site(model_group: Dict[str, List[Type[ModelAdmin]]]):
    model_list.update(model_group)


def get_model_site(resource: str) -> Optional[Type[ModelAdmin]]:
    for m_l in model_list.values():
        for i in m_l:
            if i.name() == resource:
                return i
    return None
