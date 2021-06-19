from typing import Dict, List, Optional, Tuple, Type

from pydantic.main import BaseModel
from tortoise import Model

from fast_tmp.admin.schema.actions import AjaxAction, DialogAction
from fast_tmp.admin.schema.crud import CRUD
from fast_tmp.admin.schema.enums import ButtonLevelEnum
from fast_tmp.admin.schema.forms import Column, Control, Form
from fast_tmp.admin.schema.frame import Dialog
from fast_tmp.admin.schema.page import AppPage, AppPageGroup, Page
from fast_tmp.admin.utils import get_columns_from_model, get_controls_from_model
from fast_tmp.models import Permission


class PageGroup:
    label: str
    children: List["AbstractCRUD"]

    def __init__(self, label: str, children: List["AbstractCRUD"]):
        self.label = label
        self.children = children

    def dict(self, user_perms: List[Permission], exclude_none=False):
        return {
            "label": self.label,
            "children": [
                child.get_AppPage(user_perms).dict(exclude_none=exclude_none)
                for child in self.children
            ],
        }


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
        self.page_groups: Dict[str, PageGroup] = {
            "default": PageGroup(label="default", children=[])
        }
        self.abstract_cruds = {}
        self.prefix = prefix
        self.page_list = []
        self.name = name
        self.logo = logo

    def dict(self, user_perms: List[Permission]):
        res = []
        for group_name, group in self.page_groups.items():
            res.append(group.dict(user_perms=user_perms, exclude_none=True))
        return res

    def add_page(self, page: "AbstractCRUD", group_name: str = "default"):
        self.page_groups[group_name].children.append(page)
        self.abstract_cruds[page.name] = page

    async def check_permission(self):
        """
        初始化权限
        """
        for group_name, page_group in self.page_groups.items():
            for page in page_group.children:
                await Permission.get_or_create(
                    codename=f"create_{page.name}", defaults={"label": f"create_{page.name}"}
                )
                await Permission.get_or_create(
                    codename=f"update_{page.name}", defaults={"label": f"update_{page.name}"}
                )
                await Permission.get_or_create(
                    codename=f"delete_{page.name}", defaults={"label": f"delete_{page.name}"}
                )
                await Permission.get_or_create(
                    codename=f"read_{page.name}", defaults={"label": f"read_{page.name}"}
                )

    def add_page_group(self, group: PageGroup):
        self.page_groups[group.label] = group

    def get_Page(self, model_name) -> "AbstractCRUD":
        for group_name, page_group in self.page_groups.items():
            for page in page_group.children:
                if page.name == model_name:
                    return page
        else:
            raise ModuleNotFoundError(f"Can't found {model_name}")  # fixme:完善报错信息为http类型

    def get_AbstractCRUD(self, name):
        return self.abstract_cruds[name]


class AbstractCRUD:
    def __init__(
        self,
        model: Type[Model],
        prefix: str = "/admin",
        create_include: Tuple[str, ...] = (),
        create_exclude: Tuple[str, ...] = (),
        create_extra_fields: Dict[str, Control] = None,
        up_include: Tuple[str, ...] = (),
        up_exclude: Tuple[str, ...] = (),
        up_extra_fields: Dict[str, Control] = None,
        list_include: Tuple[str, ...] = (),
        list_exclude: Tuple[str, ...] = (),
        list_extra_fields: Dict[str, Column] = None,
    ):
        """
        抽象crud-json生成
        """
        self.body = {}
        self.model = model
        self.prefix = prefix
        self.name = model.__name__
        self.list_include = list_include
        self.list_exclude = list_exclude
        self.up_include = up_include
        self.up_exclude = up_exclude
        self.create_include = create_include
        self.create_exclude = create_exclude
        self.perm_body = {}
        self.up_extra_fields = up_extra_fields
        self.create_extra_fields = create_extra_fields
        self.list_extra_fields = list_extra_fields

    def _create_crud(self, methods):
        body = []
        buttons = []
        if "Create" in methods:
            body.append(
                DialogAction(
                    label="新增",
                    dialog=Dialog(
                        title="新增",
                        body=Form(
                            name=f"新增{self.name}",
                            title=f"新增{self.name}",
                            controls=get_controls_from_model(
                                self.model,
                                include=self.create_include,
                                exclude=self.create_exclude,
                                extra_fields=self.create_extra_fields,
                            ),
                            primaryField=self.model._meta.pk_attr,
                            api=f"post:{self.prefix}/{self.name}/create",
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
                            name=f"修改{self.name}",
                            controls=get_controls_from_model(
                                self.model,
                                include=self.up_include,
                                exclude=self.up_exclude,
                                extra_fields=self.up_extra_fields,
                            ),
                            api="put:" + self.prefix + "/" + self.name + "/update/${id}",
                            initApi="get:" + self.prefix + "/" + self.name + "/update/${id}",
                            primaryField=self.model._meta.pk_attr,
                        ),
                    ),
                )
            )

        if "Delete" in methods:
            buttons.append(
                AjaxAction(
                    api="delete:" + self.prefix + "/" + self.name + "/delete/${id}",
                    label="删除",
                    level=ButtonLevelEnum.danger,
                )
            )

        if "List" in methods:
            columns = get_columns_from_model(
                self.model,
                include=self.list_include,
                exclude=self.list_exclude,
                extra_fields=self.list_extra_fields,
            )
            columns.extend(buttons)
            body.append(
                CRUD(
                    api="get:" + self.prefix + "/" + self.name + "/list",
                    columns=columns,
                )
            )
        if "DeleteMany" in methods:
            pass
        return body

    def get_AppPage(self, user_perms: List[Permission]):
        codenames = [user_perm.codename for user_perm in user_perms]
        perm_code = "-".join(codenames)
        if perm_code == "" or f"read_{self.name}" not in codenames:
            return BaseModel()
        if not self.perm_body.get(perm_code):
            methods = []
            for user_perm in user_perms:
                if user_perm.codename == f"create_{self.name}":
                    methods.append("Create")
                elif user_perm.codename == f"read_{self.name}":
                    methods.append("List")
                elif user_perm.codename == f"update_{self.name}":
                    methods.append("Update")
                elif user_perm.codename == f"delete_{self.name}":
                    methods.append("Delete")
            body = self._create_crud(methods)
            self.perm_body[perm_code] = body

        return AppPage(
            label=self.name,
            icon="",
            url=self.prefix + "/" + self.name,
            schema=Page(title=self.name, body=self.perm_body.get(perm_code))
            # schemaApi="get:" + self.prefix + "/" + self.model.__name__ + "/schema",
        )
