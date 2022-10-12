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
        await self.login(
            "user1",
        )
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
