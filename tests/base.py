from fastapi import FastAPI
from httpx import AsyncClient
from tortoise import Tortoise
from tortoise.contrib.test import SimpleTestCase

from fast_tmp.conf import settings
from fast_tmp.factory import create_app
from fast_tmp.models import Permission, User
from fast_tmp.site import register_model_site

from .admin import AuthorModel, BookModel, RoleModel

register_model_site({"fieldtesting": [RoleModel(), BookModel(), AuthorModel()]})
app = create_app()


class BaseSite(SimpleTestCase):
    client: AsyncClient
    app: FastAPI = app

    async def asyncSetUp(self) -> None:
        self.client = AsyncClient(app=self.app, base_url="http://test")
        await self.client.__aenter__()
        await Tortoise.init(settings.TORTOISE_ORM, _create_db=True)
        await Tortoise.generate_schemas()
        await self.create_superuser("admin", "admin")
        await self.migrate_permissions()

    async def asyncTearDown(self) -> None:
        await self.client.__aexit__()
        await Tortoise.close_connections()

    @classmethod
    async def create_user(
        cls, username: str, password="123456", is_superuser=False, is_active=True, is_staff=True
    ):
        user = User(
            username=username,
            is_superuser=is_superuser,
            is_active=is_active,
            is_staff=is_staff,
            name=username,
        )
        if await User.filter(username=user.username).exists():
            return
        user.set_password(password)
        await user.save()
        return user

    @classmethod
    async def create_superuser(cls, username, password):
        if await User.filter(username=username).exists():
            return
        user = User(
            username=username, is_superuser=True, is_active=True, is_staff=True, name=username
        )
        user.set_password(password)
        await user.save()

    async def migrate_permissions(self):
        await Permission.migrate_permissions()

    async def login(self):
        response = await self.client.post(
            "/admin/login",
            headers={"ContentType": "application/x-www-form-urlencoded"},
            data={"username": "admin", "password": "admin"},
        )
        assert response.status_code == 302
        assert response.headers.get("location") == "http://test/admin/"
