from tortoise.expressions import Q

from fast_tmp.models import Group, Permission, User

from .base import BaseSite


class TestPermission(BaseSite):
    """
    测试权限
    """

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
                "status": 0,
                "msg": "",
                "data": {
                    "pages": [
                        {"label": "book", "url": "/", "redirect": "Book"},
                        {
                            "label": "fieldtesting",
                            "children": [
                                {"label": "role", "url": "Role", "schemaApi": "Role/schema"},
                                {"label": "book", "url": "Book", "schemaApi": "Book/schema"},
                                {"label": "author", "url": "Author", "schemaApi": "Author/schema"},
                            ],
                        },
                    ]
                },
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
                "status": 0,
                "msg": "",
                "data": {
                    "pages": [
                        {"label": "book", "url": "/", "redirect": "Book"},
                        {
                            "label": "fieldtesting",
                            "children": [
                                {"label": "role", "url": "Role", "schemaApi": "Role/schema"},
                                {"label": "book", "url": "Book", "schemaApi": "Book/schema"},
                                {"label": "author", "url": "Author", "schemaApi": "Author/schema"},
                            ],
                        },
                    ]
                },
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
                                    "label": "作者",
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
            {"status": 0, "msg": "", "data": {"value": "/media/book/cover/avatar1.jpeg"}},
        )
        data = {
            "name": "book1",
            "author": 1,
            "rating": 123,
            "cover": "/media/book/cover/avatar1.jpeg",
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
                            "cover": "/media/book/cover/avatar1.jpeg",
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
        await Permission.filter(codename__startswith="book").delete()
        perms = await Permission.all().values("codename")
        perms = {perm["codename"] for perm in perms}
        self.assertEqual(
            perms,
            {
                "tournament_delete",
                "team_create",
                "author_list",
                "author_create",
                "address_delete",
                "address_create",
                "tree_create",
                "event_list",
                "tree_update",
                "user_update",
                "tournament_create",
                "address_update",
                "event_update",
                "user_delete",
                "node_create",
                "author_update",
                "address_list",
                "tournament_list",
                "node_delete",
                "node_list",
                "team_list",
                "user_list",
                "reporter_list",
                "reporter_update",
                "group_delete",
                "tree_list",
                "reporter_delete",
                "permission_delete",
                "group_list",
                "tree_delete",
                "role_update",
                "role_delete",
                "role_list",
                "author_delete",
                "group_update",
                "role_create",
                "team_delete",
                "user_create",
                "permission_list",
                "reporter_create",
                "team_update",
                "group_create",
                "event_delete",
                "node_update",
                "permission_update",
                "tournament_update",
                "permission_create",
                "event_create",
            },
        )
        response = await self.client.post("/admin/Permission/extra/migrate")
        self.assertEqual(
            response.json(), {"status": 0, "msg": "success update table permission", "data": {}}
        )
        perms2 = await Permission.all().values("codename")
        perms2 = {perm["codename"] for perm in perms2}
        self.assertEqual(
            perms2,
            {
                "tournament_delete",
                "team_create",
                "author_list",
                "author_create",
                "address_delete",
                "address_create",
                "tree_create",
                "event_list",
                "tree_update",
                "user_update",
                "tournament_create",
                "address_update",
                "event_update",
                "user_delete",
                "node_create",
                "author_update",
                "booknoconstraint_update",
                "address_list",
                "tournament_list",
                "book_update",
                "booknoconstraint_list",
                "book_delete",
                "node_delete",
                "node_list",
                "team_list",
                "user_list",
                "reporter_list",
                "reporter_update",
                "book_create",
                "booknoconstraint_create",
                "group_delete",
                "tree_list",
                "reporter_delete",
                "booknoconstraint_delete",
                "permission_delete",
                "group_list",
                "tree_delete",
                "role_update",
                "role_delete",
                "role_list",
                "author_delete",
                "group_update",
                "role_create",
                "team_delete",
                "user_create",
                "permission_list",
                "reporter_create",
                "team_update",
                "group_create",
                "event_delete",
                "node_update",
                "permission_update",
                "tournament_update",
                "permission_create",
                "event_create",
                "book_list",
            },
        )
