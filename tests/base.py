from fastapi import FastAPI
from httpx import AsyncClient
from tortoise import Tortoise
from tortoise.contrib.test import SimpleTestCase

from fast_tmp.conf import settings
from fast_tmp.factory import create_app
from fast_tmp.models import User, Permission
from fast_tmp.site import register_model_site
from fast_tmp.utils.model import get_all_models
from fast_tmp_cli import make_permissions

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
        await Tortoise.generate_schemas()
        await self.create_superuser("admin", "admin")
        await self.make_permissions()

    async def asyncTearDown(self) -> None:
        await self.client.__aexit__()
        await Tortoise.close_connections()

    @classmethod
    async def create_superuser(cls, username, password):
        if await User.filter(username=username).exists():
            return
        user = User(
            username=username, is_superuser=True, is_active=True, is_staff=True, name=username
        )
        user.set_password(password)
        await user.save()

    async def make_permissions(self):
        all_model = get_all_models()
        for model in all_model:
            model_name = model.__name__.lower()
            await Permission.get_or_create(codename=model_name + "_create", defaults={"label": f"{model_name}_创建"})
            await Permission.get_or_create(codename=model_name + "_update", defaults={"label": f"{model_name}_更新"})
            await Permission.get_or_create(codename=model_name + "_delete", defaults={"label": f"{model_name}_删除"})
            await Permission.get_or_create(codename=model_name + "_list", defaults={"label": f"{model_name}_查看"})

    async def login(self):
        response = await self.client.post(
            "/admin/login",
            headers={"ContentType": "application/x-www-form-urlencoded"},
            data={"username": "admin", "password": "admin"},
        )
        assert response.status_code == 302
        assert response.headers.get("location") == "http://test/admin/"
