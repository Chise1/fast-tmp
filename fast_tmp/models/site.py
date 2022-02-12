from typing import Any

from sqlalchemy.orm import Session

from fast_tmp.models import Group, User
from fast_tmp.site import ModelAdmin


class UserAdmin(ModelAdmin):
    model = User
    list_display = (User.id, User.username, User.is_active)
    create_fields = (User.username, User.password)
    update_fields = (User.password,)

    @classmethod
    def create_model(cls, data: dict, session: Session) -> Any:
        user = super().create_model(data, session)
        user.set_password(data["password"])
        return user

    @classmethod
    def update_model(cls, model: User, data: dict, session: Session) -> Any:
        super().update_model(model, data, session)
        model.set_password(data["password"])
        return model


class GroupAdmin(ModelAdmin):
    model = Group
    list_display = (Group.id, Group.name, Group.users)
    create_fields = (Group.name, Group.users)
    update_fields = (Group.name, Group.users)
