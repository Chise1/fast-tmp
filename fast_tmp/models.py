import enum
from typing import Set

from tortoise import Model, fields


class Permission(Model):
    """
    权限
    """

    label = fields.CharField(max_length=128, description="权限名")
    codename = fields.CharField(max_length=128, unique=True, description="权限码")
    groups: fields.ManyToManyRelation["Group"]
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

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
        from fast_tmp.site import model_list

        for models in model_list.values():
            for model in models:
                name = model.name
                prefix = model.prefix
                await cls.get_or_create(
                    codename=f"{prefix}_list", defaults={"label": f"{name}_list"}
                )
                await cls.get_or_create(
                    codename=f"{prefix}_create", defaults={"label": f"{name}_create"}
                )
                await cls.get_or_create(
                    codename=f"{prefix}_update", defaults={"label": f"{name}_update"}
                )
                await cls.get_or_create(
                    codename=f"{prefix}_delete", defaults={"label": f"{name}_delete"}
                )
        return True


class User(Model):
    """
    用户
    """

    username = fields.CharField(max_length=128, unique=True, description="用户名")
    password = fields.CharField(max_length=255, description="密码")
    name = fields.CharField(max_length=128, description="名称")
    avatar = fields.CharField(max_length=255, null=True, description="头像(base64)")
    is_active = fields.BooleanField(default=True, description="活跃(False则账户无法使用)")
    is_staff = fields.BooleanField(default=False, description="职员(False则无法登录管理界面)")
    is_superuser = fields.BooleanField(default=False, description="超级管理员")
    groups: fields.ManyToManyRelation["Group"]
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

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
        """
        获取用户权限
        """
        if self.is_superuser:
            return codenames
        perms = await Permission.filter(groups__users=self, codename__in=codenames)
        return set(i.codename for i in perms)

    def __str__(self):
        return self.name


class Group(Model):
    """
    组
    """

    name = fields.CharField(max_length=128, unique=True, description="组名")
    permissions: fields.ManyToManyRelation[Permission] = fields.ManyToManyField(
        "fast_tmp.Permission", related_name="groups", description="权限"
    )
    users: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "fast_tmp.User", related_name="groups", description="用户"
    )
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name


class Operate(enum.IntEnum):
    login = 1
    create = 2
    update = 3
    delete = 4


class OperateRecord(Model):
    """
    操作记录
        登录记录
        修改记录
        创建记录
        删除记录
    除了登录记录，其他记录存储json格式
    """

    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "fast_tmp.User", related_name="login_record"
    )
    operate = fields.IntEnumField(Operate, description="operate")
    schema = fields.CharField(max_length=255, null=True, description="修改对象")  # 模型名称
    schema_id = fields.IntField(null=True)  # 模型ID
    old = fields.TextField(null=True, description="修改前数据")
    new = fields.TextField(null=True, description="修改后数据")
    create_time = fields.DatetimeField(auto_now_add=True, description="修改时间")

    @classmethod
    async def login(cls, user: User):
        """
        记录登录信息
        """
        try:
            await cls.create(user=user, operate=Operate.login)
        except Exception as e:
            print(e)

    class Meta:
        ordering = ("-create_time",)
