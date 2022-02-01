from typing import Container, List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, select
from sqlalchemy.orm import Session, declarative_base, joinedload, relationship

from fast_tmp.utils.password import make_password, verify_password

Base = declarative_base()

group_permission = Table(
    "group_permission",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id")),
    Column("permission_code", String(128), ForeignKey("permission.code")),
)

group_user = Table(
    "group_user",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id")),
    Column(
        "user_id",
        Integer,
        ForeignKey("user.id"),
    ),
)


class AbstractModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class User(AbstractModel):
    __tablename__ = "user"

    username = Column(String(128), unique=True)
    password = Column(String(128), nullable=True)
    is_superuser = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=True)

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
        :param raw_password:
        :return:
        """
        return verify_password(raw_password, self.password)

    def has_perm(self, session: Session, perm: str) -> bool:
        """
        判定用户是否有权限
        """
        if self.is_superuser:
            return True
        results = session.execute(
            select(Group.id)
                .join(Group.users.and_(User.id == self.id))
                .join(Group.permissions.and_(Permission.code == perm))
        ).all()
        if len(results) > 0:
            return True
        return False

    # todo:需要测试
    def has_perms(self, session: Session, perms: Container[str]) -> bool:
        """
        根据permission的codename进行判定
        """
        if self.is_superuser:
            return True
        results = session.execute(
            select(Group.id)
                .join(Group.users.and_(User.id == self.id))
                .join(Group.permissions.and_(Permission.code.in_(perms)))
        ).all()
        if len(results) > 0:
            return True
        return False

    def perms(self, session: Session) -> List[str]:
        """
        获取用户的所有权限
        """
        groups = (
            session.execute(
                select(Group)
                    .options(joinedload(Group.permissions))
                    .join(Group.users)
                    .filter(User.id == self.id)
            )
                .scalars()
                .all()
        )
        permissions = []
        for group in groups:
            for p in group.permissions:
                permissions.append(p.code)
        return permissions

    def __str__(self):
        return self.username


class Group(AbstractModel):
    __tablename__ = "group"
    name = Column(String(32))
    permissions: "Permission" = relationship(
        "Permission", secondary="group_permission", backref="groups", cascade="all,delete"
    )
    users = relationship("User", secondary="group_user", backref="groups", cascade="all,delete")

    def get_perms(self, db_session: Session) -> List[str]:
        permissions = db_session.execute(
            select(group_permission).where(group_permission.c.group_id == self.id)
        ).fetchall()
        return [permission[1] for permission in permissions]

    def get_users(self, session: Session) -> List[User]:
        results = session.execute(
            select(Group).options(joinedload(Group.users)).where(Group.id == self.id)
        )
        return results.scalars().first().users


class Permission(Base):
    __tablename__ = "permission"
    code = Column(String(128), primary_key=True)
    name = Column(String(128))

    def __str__(self):
        return self.name + "-" + self.code

