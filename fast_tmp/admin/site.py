from typing import Iterable, List, Optional

from starlette.requests import Request

from fast_tmp.admin.depends import active_user_or_none
from fast_tmp.amis.actions import AjaxAction
from fast_tmp.amis.base import _Action
from fast_tmp.amis.crud import CRUD
from fast_tmp.amis.formitem import FormItem
from fast_tmp.amis.forms import Form
from fast_tmp.amis.page import Page
from fast_tmp.amis.view.divider import Divider
from fast_tmp.exceptions import NoAuthError, NotFoundError
from fast_tmp.models import Group, OperateRecord, Permission, User
from fast_tmp.responses import AdminRes, ListDataWithPage
from fast_tmp.site import ModelAdmin
from fast_tmp.site.field import Password


class UserAdmin(ModelAdmin):
    model = User
    list_display = ("id", "name", "username", "is_active", "is_superuser", "is_staff")
    ordering = ("id", "name", "username")
    inline = ("is_active", "is_superuser", "is_staff")
    create_fields = (
        "username",
        "password",
        "name",
        "groups",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    update_fields = (
        "username",
        "password",
        "name",
        "groups",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    fields = {
        "password": Password(label="密码", name="password", null=True, default="")
    }  # type: ignore


class GroupAdmin(ModelAdmin):
    model = Group
    list_display = ("name", "users", "permissions")
    ordering = ("name",)
    create_fields = ("name", "users", "permissions")
    update_fields = ("name", "users", "permissions")


class PermissionAdmin(ModelAdmin):
    model = Permission
    list_display = ("label", "codename", "groups")
    create_fields = ("label", "codename", "groups")
    update_fields = ("label", "codename", "groups")

    def get_create_dialogation_button(
        self, request: Request, codenames: Iterable[str]
    ) -> List[_Action]:
        buttons = super().get_create_dialogation_button(request, codenames)
        buttons.append(AjaxAction(label="同步权限", api=f"post:{self.prefix}/extra/migrate"))
        return buttons

    async def router(self, request: Request, resource: str, method: str) -> AdminRes:
        if await self.model.migrate_permissions():
            return AdminRes(msg="success update table permission")
        else:
            return AdminRes(msg="success update table failed")


# todo 需要完善创建、更新和删除的操作记录
class OperateRecordAdmin(ModelAdmin):
    """
    操作记录
    """

    model = OperateRecord
    list_display = ("user", "operate", "old", "new", "create_time")
    ordering = ("user", "operate", "create_time")
    methods = ("list",)

    async def list(
        self,
        request: Request,
        perPage: int = 10,
        page: int = 1,
        orderBy: Optional[str] = None,
        orderDir: Optional[str] = None,
    ) -> ListDataWithPage:
        user = request.user

        if user.is_superuser:  # 超管看所有操作，其他人看自己操作
            queryset = OperateRecord.all()
        else:
            queryset = OperateRecord.filter(user=user)
        count = await queryset.count()
        queryset = queryset.select_related("user")
        if orderBy and orderBy in self.ordering:
            queryset = queryset.order_by("-" + orderBy if orderDir == "desc" else orderBy)
        datas = await queryset.limit(perPage).offset((page - 1) * perPage)
        return ListDataWithPage(
            total=count,
            items=[
                {
                    "pk": data.pk,
                    "user": {"label": str(data.user), "value": str(data.user)},
                    "operate": data.operate.name,
                    "old": data.old,
                    "new": data.new,
                    "create_time": data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for data in datas
            ],
        )


class UserInfo(ModelAdmin):
    """
    查看和修改用户自己的信息
    """

    model = OperateRecord
    list_display = ("create_time", "schema", "operate", "schema_id", "old", "new")
    ordering = ("create_time", "schema", "schema_id")
    methods = ("list",)

    async def list(
        self,
        request: Request,
        perPage: int = 10,
        page: int = 1,
        orderBy: Optional[str] = None,
        orderDir: Optional[str] = None,
    ) -> ListDataWithPage:
        base_queryset = self.queryset(request)
        base_queryset = self.queryset_filter(request, base_queryset)
        base_queryset = base_queryset.filter(user=request.user)  # 只读取自己的数据
        queryset = self.prefetch(request, base_queryset, self.get_list_distplay())
        if orderBy and orderBy in self.ordering:
            queryset = queryset.order_by("-" + orderBy if orderDir == "desc" else orderBy)
        datas = await queryset.limit(perPage).offset((page - 1) * perPage)
        res = []
        for i in datas:
            ret = {}
            for field_name, field in self.get_list_display_with_pk().items():
                if field._many:
                    continue
                ret[field_name] = await field.get_value(request, i)
            res.append(ret)
        count = await base_queryset.count()
        return ListDataWithPage(total=count, items=res)

    async def get_app_page(self, request: Request) -> Page:
        return Page(
            title="个人信息",
            body=[
                Form(
                    label="个人信息",
                    initApi="get:self/extra/info",
                    api="put:self/extra/info",
                    body=[
                        FormItem(type="input-text", name="name", label="名字"),
                        Password(label="密码", name="password", null=True, default="").get_formitem(
                            request, []
                        ),
                    ],
                ),
                Divider(),
                self.get_crud(request, []),
            ],
        )

    @property
    def site(self):
        return {
            "label": self.name,
            "url": self.prefix,
            "schemaApi": self.prefix + "/schema",
            "visible": False,  # 不显示在菜单中
        }

    def get_crud(self, request: Request, codenames: List[str]):
        return CRUD(
            api=self._prefix + "/list",
            columns=self.get_list_fields(request),
            quickSaveItemApi=self._prefix + "/patch/" + "$pk",
            syncLocation=False,
        )

    async def router(self, request: Request, resource: str, method: str) -> AdminRes:
        user = await active_user_or_none(request.cookies.get("access_token"))
        if not user or not user.is_staff:
            raise NoAuthError()
        if resource == "info":
            if method == "GET":
                return AdminRes(data={"name": user.name, "password": ""})
            if method == "PUT":
                data = await request.json()
                if data.get("name"):
                    user.name = data["name"]
                if data.get("password"):
                    user.set_password(data["password"])
                await user.save()
                return AdminRes(msg="修改成功")
        raise NotFoundError("not found function.")
