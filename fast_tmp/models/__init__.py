from typing import Any, List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import declarative_base

from fast_tmp.utils.password import make_password, verify_password

Base: Any = declarative_base()

group_permission = Table(
    "auth_group_permission",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("auth_group.id")),
    Column("permission_code", String(128), ForeignKey("auth_permission.code")),
)

group_user = Table(
    "auth_group_user",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("auth_group.id")),
    Column("auth_user_id", Integer, ForeignKey("auth_user.id")),
)


class AbstractModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class User(AbstractModel):
    __tablename__ = "auth_user"

    username = Column(String(128), unique=True)
    password = Column(String(128), nullable=True)
    is_superuser = Column(Boolean(), default=False)
    is_manager = Column(Boolean(), default=False)  # could login admin
    is_active = Column(Boolean(), default=True)
    groups: List["Group"] = relationship(
        "Group", secondary="auth_group_user", back_populates="users", cascade="all,delete"
    )

    def set_password(self, raw_password: str):
        """
        设置密码
        :param raw_password:
        :return:
        """
        self.password = make_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """
        验证密码
        """
        return verify_password(raw_password, self.password)

    # def has_perm(
    #     self,
    #     perm: str,
    #     session: Session,
    # ) -> bool:
    #     """
    #     判定用户是否有权限
    #     """
    #     if self.is_superuser:
    #         return True
    #     results = session.execute(
    #         select(Group.id)
    #         .join(Group.users.and_(User.id == self.id))
    #         .join(Group.permissions.and_(Permission.code == perm))
    #     ).all()
    #     if len(results) > 0:
    #         return True
    #     return False

    # todo:need test
    # def has_perms(self, session: Session, perms: Set[str]) -> bool:
    #     """
    #     根据permission的codename进行判定
    #     """
    #     if self.is_superuser:
    #         return True
    #     results = session.execute(
    #         select(Permission.code)
    #         .join(Group.permissions.and_(Permission.code.in_(perms)))
    #         .join(Group.users.and_(User.id == self.id))
    #     )
    #     # results = session.execute(
    #     #     select(Group.id)
    #     #         .join(Group.users.and_(User.id == self.id))
    #     #         .join(Group.permissions.and_(Permission.code.in_(perms)))
    #     # ).all()
    #     if len(results) == len(perms):
    #         return True
    #     return False

    # def perms(self, session: Session) -> List[str]:
    #     """
    #     获取用户的所有权限
    #     """
    #     groups = (
    #         session.execute(
    #             select(Group)
    #             .options(joinedload(Group.permissions))
    #             .join(Group.users)
    #             .filter(User.id == self.id)
    #         )
    #         .scalars()
    #         .all()
    #     )
    #     permissions = []
    #     for group in groups:
    #         for p in group.permissions:
    #             permissions.append(p.code)
    #     return permissions

    # def __str__(self):
    #     return self.username


class Permission(Base):
    __tablename__ = "auth_permission"
    code = Column(String(128), primary_key=True)
    name = Column(String(128))

    # def __str__(self):
    #     return self.name + "-" + self.code


class Group(AbstractModel):
    __tablename__ = "auth_group"
    name = Column(String(32))
    permissions: List[Permission] = relationship(
        "Permission", secondary="auth_group_permission", backref="groups", cascade="all,delete"
    )
    users: List[User] = relationship(
        "User", secondary="auth_group_user", back_populates="groups", cascade="all,delete"
    )

    # def get_perms(self, db_session: Session) -> List[str]:
    #     permissions = db_session.execute(
    #         select(group_permission).where(group_permission.c.group_id == self.id)
    #     ).fetchall()
    #     return [permission[1] for permission in permissions]

    # def get_users(self, session: Session) -> List[User]:
    #     results = session.execute(
    #         select(Group).options(joinedload(Group.users)).where(Group.id == self.id)
    #     )
    #     return results.scalars().first().users
