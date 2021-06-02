from typing import Dict, Optional, Tuple, Type

from tortoise import Model

from fast_tmp.admin.schema.actions import AjaxAction, DialogAction
from fast_tmp.admin.schema.crud import CRUD
from fast_tmp.admin.schema.enums import ButtonLevelEnum
from fast_tmp.admin.schema.forms import Form
from fast_tmp.admin.schema.frame import Dialog
from fast_tmp.admin.schema.page import App, AppPage, AppPageGroup


class AbstractApp:
    app: App
    page_groups: Dict[str, AppPageGroup]
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        name: str,
        logo: Optional[str],
        prefix: str = "",
    ):
        self.app = App(
            brandName=name,
            pages=[],
            logo=logo,
        )
        self.page_groups = {"default": AppPageGroup(label="default", children=[])}
        self.pages = {}
        self.prefix = prefix

    def get_json(self):
        self.app.pages = [i for i in self.page_groups]
        return self.app.json()

    def add_page(self, page: AppPage, group_name: str = "default"):
        self.page_groups[group_name].children.append(page)

    def add_page_group(self, group: AppPageGroup):
        self.page_groups[group.label] = group

    def get_page(self, model_name) -> AppPage:
        for group_name, page_group in self.page_groups.items():
            for page in page_group.children:
                if page.label == model_name:
                    return page
        else:
            raise ModuleNotFoundError(f"Can't found {model_name}")  # fixme:完善报错信息为http类型


from fast_tmp.admin.utils import get_columns_from_model, get_controls_from_model


class AbstractCRUD:
    body = []

    def __init__(
        self,
        model: Type[Model],
        create_include: Tuple[str, ...] = (),
        create_exclude: Tuple[str, ...] = (),
        up_include: Tuple[str, ...] = (),
        up_exclude: Tuple[str, ...] = (),
        list_include: Tuple[str, ...] = (),
        list_exclude: Tuple[str, ...] = (),
        methods: Tuple[str, ...] = ("List", "Retrieve", "Create", "Update", "Delete", "DeleteMany"),
    ):
        """
        抽象crud-json生成
        """
        buttons = []
        if "Create" in methods:
            self.body.append(
                DialogAction(
                    label="新增",
                    dialog=Dialog(
                        title="新增",
                        body=Form(
                            name=f"新增{model.__name__}",
                            controls=get_controls_from_model(
                                model, include=create_include, exclude=create_exclude
                            ),
                            api=f"post:{model.__name__}/create",
                        ),
                    ),
                )
            )
        if "Update" in methods:
            buttons.append(
                DialogAction(
                    label="修改",
                    dialog=Dialog(
                        title="修改",
                        body=Form(
                            name=f"修改{model.__name__}",
                            controls=get_controls_from_model(
                                model, include=up_include, exclude=up_exclude
                            ),
                            api="put:" + model.__name__ + "/up/${id}",
                            initApi="get:" + model.__name__ + "/up?id=${id}",
                        ),
                    ),
                )
            )
        if "Delete" in methods:
            buttons.append(
                AjaxAction(
                    api="delete:" + model.__name__ + "/delete/${id}",
                    label="删除",
                    level=ButtonLevelEnum.danger,
                )
            )
        if "List" in methods:
            self.body.append(
                CRUD(
                    api="get:" + model.__name__ + "/list",
                    columns=get_columns_from_model(
                        model, include=list_include, exclude=list_exclude
                    ).extend(buttons),
                )
            )
        if "DeleteMany" in methods:
            # fixme:尚未实现
            pass
