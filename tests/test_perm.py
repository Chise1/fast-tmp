from fast_tmp.models import Group, Permission, User

from .base import BaseSite


class TestPermission(BaseSite):
    """
    测试权限
    """

    async def test_perm(self):
        user: User = await self.create_user(
            "user1",
        )
        group = Group(name="group1")
        await group.save()
        await group.users.add(user)
        perms = await Permission.filter(codename__startswith="book")
        await group.permissions.add(*perms)
        assert await user.has_perm("book_list")
        assert await user.has_perms({"book_list", "book_create"})
