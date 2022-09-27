from fastapi import FastAPI
from httpx import AsyncClient
from tortoise import Tortoise
from tortoise.contrib.test import SimpleTestCase

from fast_tmp.conf import settings
from fast_tmp.factory import create_app
from fast_tmp.models import User
from fast_tmp.site import register_model_site

from .admin import RoleModel

register_model_site({"fieldtesting": [RoleModel()]})
app = create_app()


class BaseSite(SimpleTestCase):
    client: AsyncClient
    app: FastAPI = app

    async def asyncSetUp(self) -> None:
        self.client = AsyncClient(app=self.app, base_url="http://test")
        await self.client.__aenter__()
        await Tortoise.init(settings.TORTOISE_ORM, _create_db=True)
        await Tortoise.generate_schemas(False)
        await self.create_superuser("admin", "admin")

    async def asyncTearDown(self) -> None:
        await self.client.__aexit__()
        await Tortoise.close_connections()

    @classmethod
    async def create_superuser(cls, username, password):
        if await User.filter(username=username).exists():
            return
        user = User(username=username, is_superuser=True)
        user.set_password(password)
        await user.save()

    async def login(self):
        response = await self.client.post(
            "/admin/login",
            headers={"ContentType": "application/x-www-form-urlencoded"},
            data={"username": "admin", "password": "admin"},
        )
        assert response.status_code == 302
        assert response.headers.get("location") == "http://test/admin/"
