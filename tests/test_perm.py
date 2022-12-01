from datetime import timedelta

from tortoise.expressions import Q

from fast_tmp.models import Group, Permission, User
from fast_tmp.utils.token import create_access_token

from .base import BaseSite

all_perms = {
    "address_create",
    "address_delete",
    "address_list",
    "address_update",
    "author_create",
    "author_delete",
    "author_list",
    "author_update",
    "booknoconstraint_create",
    "booknoconstraint_delete",
    "booknoconstraint_list",
    "booknoconstraint_update",
    "dec_create",
    "dec_delete",
    "dec_list",
    "dec_update",
    "event_create",
    "event_delete",
    "event_list",
    "event_update",
    "group_create",
    "group_delete",
    "group_list",
    "group_update",
    "intenumfield_create",
    "intenumfield_delete",
    "intenumfield_list",
    "intenumfield_update",
    "node_create",
    "node_delete",
    "node_list",
    "node_update",
    "permission_create",
    "permission_delete",
    "permission_list",
    "permission_update",
    "reporter_create",
    "reporter_delete",
    "reporter_list",
    "reporter_update",
    "role_create",
    "role_delete",
    "role_list",
    "role_update",
    "team_create",
    "team_delete",
    "team_list",
    "team_update",
    "tournament_create",
    "tournament_delete",
    "tournament_list",
    "tournament_update",
    "tree_create",
    "tree_delete",
    "tree_list",
    "tree_update",
    "user_create",
    "user_delete",
    "user_list",
    "user_update",
}


class TestPermission(BaseSite):
    """
    测试权限
    """

    async def test_token(self):
        """
        测试token获取用户
        """
        token = create_access_token(
            data={"sub": "zhangsan", "id": 10}, expires_delta=timedelta(minutes=10)
        )
        self.client.cookies.set("access_token", token)
        response = await self.client.get("/admin/site")
        self.assertEqual(302, response.status_code)
        self.assertEqual("http://test/admin/login", response.next_request.url)
        user = await self.create_user("zhangsan", is_active=False)
        token = create_access_token(
            data={"sub": "zhangsan", "id": user.pk}, expires_delta=timedelta(minutes=10)
        )
        self.client.cookies.set("access_token", token)
        response = await self.client.get("/admin/site")
        self.assertEqual(302, response.status_code)
        self.assertEqual("http://test/admin/login", response.next_request.url)
        self.client.cookies.set("access_token", "asdfasdfasdfasdf")
        response = await self.client.get("/admin/site")
        self.assertEqual(302, response.status_code)
        self.assertEqual("http://test/admin/login", response.next_request.url)

        token = create_access_token(data={"id": 10}, expires_delta=timedelta(minutes=10))
        self.client.cookies.set("access_token", token)
        response = await self.client.get("/admin/site")
        self.assertEqual(302, response.status_code)
        self.assertEqual("http://test/admin/login", response.next_request.url)

    async def test_perm(self):
        user: User = await self.create_user("user1")
        group = Group(name="group1")
        await group.save()
        await group.users.add(user)
        perms = await Permission.filter(codename__startswith="book")
        await group.permissions.add(*perms)
        assert await user.has_perm("book_list")
        assert await user.has_perms({"book_list", "book_create"})
        await self.login("user1")
        response = await self.client.get("/admin/site")
        self.assertEqual(
            response.json(),
            {
                "data": {
                    "pages": [
                        {"label": "book", "redirect": "Book", "url": "/"},
                        {
                            "children": [
                                {"label": "book", "schemaApi": "Book/schema", "url": "Book"}
                            ],
                            "label": "fieldtesting",
                        },
                    ]
                },
                "msg": "",
                "status": 0,
            },
        )
        perms2 = []
        for p in perms:
            if p == "book_list":
                perms2.append(p)
        await group.permissions.clear()
        await group.permissions.add(*perms2)
        response = await self.client.get("/admin/site")
        self.assertEqual(
            response.json(),
            {
                "data": {
                    "pages": [
                        {"label": "book", "redirect": "Book", "url": "/"},
                        {
                            "children": [
                                {"label": "book", "schemaApi": "Book/schema", "url": "Book"}
                            ],
                            "label": "fieldtesting",
                        },
                    ]
                },
                "msg": "",
                "status": 0,
            },
        )
        response = await self.client.get("/admin/Book/schema")
        self.assertEqual(
            response.json(),
            {
                "status": 0,
                "msg": "",
                "data": {
                    "type": "page",
                    "title": "book",
                    "body": [
                        {
                            "type": "crud",
                            "api": "Book/list",
                            "columns": [
                                {"name": "name", "label": "name"},
                                {
                                    "type": "custom",
                                    "name": "author",
                                    "label": "author",
                                    "onMount": "const text = document.createTextNode(value.label);dom.appendChild(text);$author=value.value;",
                                    "onUpdate": "const value=data.author;dom.current.firstChild.textContent=value.label;$author=value.value;",
                                },
                                {"name": "rating", "label": "rating"},
                                {"label": "cover", "name": "cover", "type": "image"},
                            ],
                            "affixHeader": False,
                            "quickSaveItemApi": "Book/patch/$pk",
                            "syncLocation": False,
                            "filter": {
                                "title": "过滤",
                                "body": [
                                    {
                                        "type": "input-text",
                                        "label": "name__contains",
                                        "name": "name__contains",
                                    }
                                ],
                                "actions": [{"type": "submit", "level": "primary", "label": "查询"}],
                            },
                        }
                    ],
                },
            },
        )
        response = await self.client.get("/admin/User/list")
        self.assertEqual(
            response.json(), {"status": 400, "msg": "you have no permission", "data": {}}
        )

    async def test_book(self):
        user: User = await self.create_user("user2")
        group = Group(name="group2")
        await group.save()
        await group.users.add(user)
        perms = await Permission.filter(
            Q(codename__startswith="book") | Q(codename__startswith="author")
        )
        await group.permissions.add(*perms)
        await self.login("user2")
        # 创建author
        response = await self.client.post(
            "/admin/Author/create", json={"name": "author_name1", "birthday": "2022-10-13"}
        )
        self.assertEqual(response.status_code, 200)
        # 查询author
        response = await self.client.get("/admin/Author/list?page=1&perPage=10")
        self.assertEqual(
            response.json(),
            {
                "status": 0,
                "msg": "",
                "data": {
                    "items": [{"name": "author_name1", "birthday": "2022-10-13", "pk": 1}],
                    "total": 1,
                },
            },
        )
        # 修改作者姓名
        response = await self.client.put(
            "/admin/Author/update/1", json={"name": "author1", "birthday": "2022-10-13", "pk": 3}
        )
        self.assertEqual(response.status_code, 200)
        # 创建book
        # 上传图片
        with open("./tests/image/avatar1.jpeg", "rb") as f:
            response = await self.client.post("/admin/Book/file/cover", files={"file": f})
        self.assertEqual(
            response.json(),
            {"status": 0, "msg": "", "data": {"value": "/media/Book/cover/avatar1.jpeg"}},
        )
        data = {
            "name": "book1",
            "author": 1,
            "rating": 123,
            "cover": "/media/Book/cover/avatar1.jpeg",
        }
        response = await self.client.post("/admin/Book/create", json=data)
        self.assertEqual(response.status_code, 200)
        response = await self.client.get("/admin/Book/list?page=1&perPage=10")
        self.assertEqual(
            response.json(),
            {
                "status": 0,
                "msg": "",
                "data": {
                    "items": [
                        {
                            "name": "book1",
                            "author": {"label": "author1", "value": 1},
                            "rating": 123.0,
                            "cover": "/media/Book/cover/avatar1.jpeg",
                            "pk": 1,
                        }
                    ],
                    "total": 1,
                },
            },
        )
        # delete
        response = await self.client.delete("/admin/Book/delete/1")
        self.assertEqual(response.status_code, 200)

    async def test_auth(self):
        user: User = await self.create_user("user3")
        group = Group(name="group3")
        await group.save()
        await group.users.add(user)
        perms = await Permission.filter(
            Q(codename__startswith="user")
            | Q(codename__startswith="group")
            | Q(codename__startswith="permission")
        )
        await group.permissions.add(*perms)
        await self.login("user3")
        # create user
        response = await self.client.get("/admin/User/select/groups")
        self.assertEqual(
            response.json(),
            {"status": 0, "msg": "", "data": {"options": [{"value": 1, "label": "group3"}]}},
        )
        response = await self.client.post(
            "/admin/User/create",
            json={
                "username": "user4",
                "password": "123456",
                "name": "user4",
                "groups": str(group.pk),
                "is_active": "True",
                "is_staff": "True",
                "is_superuser": "False",
            },
        )
        self.assertEqual(response.status_code, 200)
        user4 = await User.get(username="user4")
        response = await self.client.post(
            f"/admin/User/patch/{user4.pk}",
            json={
                "is_active": "True",
                "is_staff": "True",
                "is_superuser": "False",
                "name": "user444",
                "pk": user4.pk,
                "username": "admin44",
            },
        )
        self.assertEqual(response.json(), {"status": 0, "msg": "", "data": {}})
        response = await self.client.get("/admin/User/list")
        self.assertEqual(
            response.json(),
            {
                "status": 0,
                "msg": "",
                "data": {
                    "items": [
                        {
                            "name": "admin",
                            "username": "admin",
                            "is_active": "True",
                            "is_superuser": "True",
                            "is_staff": "True",
                            "pk": 1,
                        },
                        {
                            "name": "user3",
                            "username": "user3",
                            "is_active": "True",
                            "is_superuser": "False",
                            "is_staff": "True",
                            "pk": 2,
                        },
                        {
                            "name": "user4",
                            "username": "user4",
                            "is_active": "True",
                            "is_superuser": "False",
                            "is_staff": "True",
                            "pk": 3,
                        },
                    ],
                    "total": 3,
                },
            },
        )
        await self.login("user4")
        await self.login("user3")
        # group
        response = await self.client.get("/admin/Group/list")
        self.assertEqual(
            response.json(),
            {"status": 0, "msg": "", "data": {"items": [{"name": "group3", "pk": 1}], "total": 1}},
        )
        response = await self.client.get(f"/admin/Group/select/users?pk={group.pk}")
        self.assertEqual(
            response.json(),
            {
                "status": 0,
                "msg": "",
                "data": {
                    "items": [{"value": 2, "label": "user3"}, {"value": 3, "label": "user4"}],
                    "total": 2,
                },
            },
        )
        await Permission.filter(codename__startswith="book_").delete()
        perms = await Permission.all().values("codename")
        perms = {perm["codename"] for perm in perms}
        self.assertEqual(all_perms, perms)
        response = await self.client.post("/admin/Permission/extra/migrate")
        self.assertEqual(
            response.json(), {"status": 0, "msg": "success update table permission", "data": {}}
        )
        perms2 = await Permission.all().values("codename")
        perms2 = {perm["codename"] for perm in perms2}
        new_all_perms = set()
        new_all_perms.update(all_perms)
        new_all_perms.update(
            {
                "book_create",
                "book_delete",
                "book_list",
                "book_update",
            }
        )
        self.assertEqual(new_all_perms, perms2)
