from fast_tmp.site import register_model_site

from .admin import RoleModel
from .base import BaseSite

register_model_site({"fieldtesting": [RoleModel()]})


class TestColumnField(BaseSite):
    async def test_site(self):
        await self.login()
        response = await self.client.get("/admin/site")
        assert response.status_code == 200
        data = response.json()
        # todo 增加数据验证
        assert data["status"] == 0
        response = await self.client.get("/admin/Role/schema")
        assert response.status_code == 200
        data = response.json()
        # todo 增加数据验证
        assert data["status"] == 0
        # 测试写入数据
        data = {
            "name": "John",
            "age": 18,
            "desc": "My name is John",
            "married": "False",
            "degree": "bachelor",
            "gender": "male",
            "create_time": "2022-09-27 12:41:59",
            "birthday": "2004-09-10",
            "config": '{"color":"green"}',
            "max_time_length": "00:23:19",
        }
        response = await self.client.post("/admin/Role/create", json=data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        # get数据
        response = await self.client.get("/admin/Role/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["name"] == "John"
        # update
