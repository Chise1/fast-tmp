from typing import Dict, Optional, Tuple, Type

from fast_tmp.admin.schema.actions import AjaxAction, DialogAction
from fast_tmp.admin.schema.crud import CRUD
from fast_tmp.admin.schema.enums import ButtonLevelEnum
from fast_tmp.admin.schema.forms import Form
from fast_tmp.admin.schema.frame import Dialog
from fast_tmp.admin.schema.page import AppPage, AppPageGroup, Page
# from fast_tmp.admin.utils import get_columns_from_model, get_controls_from_model


class AbstractApp:
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
        self.page_groups = {"default": AppPageGroup(label="default", children=[])}
        self.abstract_cruds = {}
        self.prefix = prefix
        self.page_list = []

    def dict(self):
        res = []
        for group_name, group in self.page_groups.items():
            res.append(group.dict(exclude_none=True))
        return res

    def add_page(self, page: "AbstractCRUD", group_name: str = "default"):
        p = page.get_AppPage()
        self.page_groups[group_name].children.append(p)
        self.abstract_cruds[page.name] = page

    def add_page_group(self, group: AppPageGroup):
        self.page_groups[group.label] = group

    def get_Page(self, model_name) -> AppPage:
        for group_name, page_group in self.page_groups.items():
            for page in page_group.children:
                if page.label == model_name:
                    return page
        else:
            raise ModuleNotFoundError(f"Can't found {model_name}")  # fixme:完善报错信息为http类型

    def get_AbstractCRUD(self, name):
        return self.abstract_cruds[name]


class AbstractCRUD:
    def __init__(
        self,
        model: type,
        prefix: str = "/admin",
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
        self.body = []
        self.model = model
        self.prefix = prefix
        self.name = model.__name__
        self.list_include = list_exclude
        self.up_include = up_include
        buttons = []
        # if "Create" in methods:
        #     self.body.append(
        #         DialogAction(
        #             label="新增",
        #             dialog=Dialog(
        #                 title="新增",
        #                 body=Form(
        #                     name=f"新增{model.__name__}",
        #                     title=f"新增{model.__name__}",
        #                     controls=get_controls_from_model(
        #                         model, include=create_include, exclude=create_exclude
        #                     ),
        #                     primaryField=model._meta.pk_attr,
        #                     api=f"post:{prefix}/{model.__name__}/create",
        #                 ),
        #             ),
        #         )
        #     )
        # if "Update" in methods:
        #     buttons.append(
        #         DialogAction(
        #             label="修改",
        #             dialog=Dialog(
        #                 title="修改",
        #                 body=Form(
        #                     name=f"修改{model.__name__}",
        #                     controls=get_controls_from_model(
        #                         model, include=up_include, exclude=up_exclude
        #                     ),
        #                     api="put:" + prefix + "/" + model.__name__ + "/update/${id}",
        #                     initApi="get:" + prefix + "/" + model.__name__ + "/update/${id}",
        #                 ),
        #             ),
        #         )
        #     )
        # if "Delete" in methods:
        #     buttons.append(
        #         AjaxAction(
        #             api="delete:" + prefix + "/" + model.__name__ + "/delete/${id}",
        #             label="删除",
        #             level=ButtonLevelEnum.danger,
        #         )
        #     )
        # if "List" in methods:
        #     columns = get_columns_from_model(model, include=list_include, exclude=list_exclude)
        #     columns.extend(buttons)
        #     self.body.append(
        #         CRUD(
        #             api="get:" + prefix + "/" + model.__name__ + "/list",
        #             columns=columns,
        #         )
        #     )
        if "DeleteMany" in methods:
            # fixme:尚未实现
            pass

    def get_AppPage(self):
        return AppPage(
            label=self.model.__name__,
            icon="",
            url=self.prefix + "/" + self.model.__name__,
            schema=Page(title=self.model.__name__, body=self.body)
            # schemaApi="get:" + self.prefix + "/" + self.model.__name__ + "/schema",
        )

    def get_Page(self):
        return Page(title=self.model.__name__, body=self.body)
