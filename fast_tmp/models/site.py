from typing import Any

from fast_tmp.models import Group, User
from fast_tmp.site import ModelAdmin


class UserAdmin(ModelAdmin):
    model = User
    list_display = (User.id, User.username, User.is_active)
    create_fields = (User.username, User.password)
    update_fields = (User.password,)

    @classmethod
    def create_model(cls, data: dict) -> Any:
        user = super().create_model(data)
        user.set_password(data["password"])
        return user

    @classmethod
    def update_model(cls, model: User, data: dict) -> Any:
        model.set_password(data["password"])
        return model


class GroupAdmin(ModelAdmin):
    model = Group
    list_display = (Group.id, Group.name)
    create_fields = (Group.name,)
    update_fields = (Group.name,)
