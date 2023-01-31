from typing import Iterable, List

from starlette.requests import Request

from fast_tmp.amis.actions import AjaxAction
from fast_tmp.amis.base import _Action
from fast_tmp.models import Group, Permission, User
from fast_tmp.responses import BaseRes
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

    async def router(self, request: Request, prefix: str, method: str) -> BaseRes:
        if await self.model.migrate_permissions():
            return BaseRes(msg="success update table permission")
        else:
            return BaseRes(msg="success update table failed")
