from typing import Iterable, List, Optional

from starlette.requests import Request

from fast_tmp.amis.actions import AjaxAction
from fast_tmp.amis.base import _Action
from fast_tmp.models import Group, OperateRecord, Permission, User
from fast_tmp.responses import BaseRes, ListDataWithPage
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
    fields = {"password": Password}  # type: ignore


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

    async def router(self, request: Request, resource: str, method: str) -> BaseRes:
        if await self.model.migrate_permissions():
            return BaseRes(msg="success update table permission")
        else:
            return BaseRes(msg="success update table failed")


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
