from typing import Sequence, Set, Tuple, Type, Union

from pydantic import BaseModel
from tortoise import Model, fields
from tortoise.expressions import Q

from fast_tmp.conf import settings


class Permission(Model):
    label = fields.CharField(max_length=128)
    codename = fields.CharField(max_length=128, unique=True)
    groups: fields.ManyToManyRelation["Group"]
    users: fields.ManyToManyRelation[f"User"]

    @classmethod
    def make_permission(
        cls,
        model: Type[BaseModel],
    ):
        """
        生成model对应的权限
        """
        model_name = model.__name__
        Permission.get_or_create(
            defaults={
                "label": "can read " + model_name,
                "model": model_name,
                "codename": "can_read_" + model_name,
            }
        )
        Permission.get_or_create(
            defaults={
                "label": "can create " + model_name,
                "model": model_name,
                "codename": "can_create_" + model_name,
            }
        )
        Permission.get_or_create(
            defaults={
                "label": "can update " + model_name,
                "model": model_name,
                "codename": "can_update_" + model_name,
            }
        )
        Permission.get_or_create(
            defaults={
                "label": "can delete " + model_name,
                "model": model_name,
                "codename": "can_delete_" + model_name,
            }
        )

    def __eq__(self, other) -> bool:
        if other == self.codename or getattr(other, "codename", None) == self.codename:
            return True
        return False

    def __str__(self):
        return self.label

    def __repr__(self):
        return self.label


class User(Model):
    username = fields.CharField(max_length=128, unique=True)
    password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    groups: fields.ManyToManyRelation["Group"]
    permissions = fields.ManyToManyField(f"fast_tmp.Permission", related_name="users")

    class Meta:
        abstract = settings.AUTH_USER_MODEL_NAME != "User"

    def set_password(self, raw_password: str):
        """
        设置密码
        """
        from fast_tmp.utils.password import make_password

        self.password = make_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """
        验证密码
        """
        from fast_tmp.utils.password import verify_password

        return verify_password(raw_password, self.password)

    async def has_perm(self, codename: str) -> bool:
        """
        判定用户是否有权限
        """
        if self.is_superuser:
            return True
        if (
            await Permission.filter(Q(users__pk=self.pk) | Q(groups__users__pk=self.pk))
            .filter(codename=codename)
            .exists()
        ):
            return True
        # if await Group.filter(users__pk=self.pk, permissions__codename=codename).exists():
        #     return True
        return False

    async def has_perms(self, codenames: Set[str]) -> bool:
        """
        根据permission的codename进行判定
        """
        if self.is_superuser:
            return True
        perms = (
            await Permission.filter(Q(users__pk=self.pk) | Q(groups__users__pk=self.pk))
            .filter(codename__in=codenames)
            .distinct()
            .values("codename")
        )
        if codenames == perms:
            return True
        return False

    def __str__(self):
        return self.username


class Group(Model):
    name = fields.CharField(max_length=128, unique=True)
    permissions = fields.ManyToManyField(f"fast_tmp.Permission", related_name="groups")
    users = fields.ManyToManyField(f"fast_tmp.User", related_name="groups")

    def __str__(self):
        return self.name
