from typing import Set

from tortoise import Model, fields


class Permission(Model):
    label = fields.CharField(max_length=128)
    codename = fields.CharField(max_length=128, unique=True)
    groups: fields.ManyToManyRelation["Group"]

    def __eq__(self, other) -> bool:
        if other == self.codename or getattr(other, "codename", None) == self.codename:
            return True
        return False

    def __str__(self):
        return self.label

    def __repr__(self):
        return self.label

    @classmethod
    async def migrate_permissions(cls) -> bool:
        """
        同步所有注册的模型的所有权限
        """
        from fast_tmp.utils.model import get_all_models

        all_models = get_all_models()
        for model in all_models:
            model_name = model.__name__.lower()
            await cls.get_or_create(
                codename=f"{model_name}_list", defaults={"label": f"{model_name}_list"}
            )
            await cls.get_or_create(
                codename=f"{model_name}_create", defaults={"label": f"{model_name}_create"}
            )
            await cls.get_or_create(
                codename=f"{model_name}_update", defaults={"label": f"{model_name}_update"}
            )
            await cls.get_or_create(
                codename=f"{model_name}_delete", defaults={"label": f"{model_name}_delete"}
            )
        return True


class User(Model):
    username = fields.CharField(max_length=128, unique=True)
    password = fields.CharField(max_length=255)
    name = fields.CharField(max_length=128)
    avatar = fields.CharField(max_length=128, null=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    groups: fields.ManyToManyRelation["Group"]

    # class Meta:
    #     abstract = settings.AUTH_USER_MODEL_NAME != "User"

    def set_password(self, raw_password: str):
        """
        设置密码
        """
        from fast_tmp.contrib.auth.hashers import make_password

        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        验证密码
        """
        from fast_tmp.contrib.auth.hashers import check_password

        return check_password(raw_password, self.password)

    async def has_perm(self, codename: str) -> bool:
        """
        判定用户是否有权限
        """
        if self.is_superuser and self.is_active:
            return True
        if await Group.filter(users__pk=self.pk, permissions__codename=codename).exists():
            return True
        return False

    async def has_perms(self, codenames: Set[str]) -> bool:
        """
        根据permission的codename进行判定
        """
        perms = await self.get_perms(codenames)
        return codenames == perms

    async def get_perms(self, codenames: Set[str]) -> Set[str]:
        if self.is_superuser:
            return codenames
        perms = await Permission.filter(groups__users=self, codename__in=codenames)
        return set(i.codename for i in perms)

    def __str__(self):
        return self.name


class Group(Model):
    name = fields.CharField(max_length=128, unique=True)
    permissions: fields.ManyToManyRelation[Permission] = fields.ManyToManyField(
        "fast_tmp.Permission", related_name="groups"
    )
    users: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "fast_tmp.User", related_name="groups"
    )

    def __str__(self):
        return self.name
