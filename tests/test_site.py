from .base import BaseSite


class TestColumnField(BaseSite):
    async def test_site(self):
        await self.login()
        response = await self.client.get("/admin/site")
        assert response.status_code == 200
        data = response.json()
        # todo 增加数据验证
        assert data["status"] == 0
        response = await self.client.get("/admin/role/schema")
        assert response.status_code == 200
        data = response.json()
        # todo 增加数据验证
        assert data["status"] == 0
        # 测试写入数据
        role_data = {
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
            "money": 10.34,
        }
        response = await self.client.post("/admin/role/create", json=role_data)
        assert response.status_code == 200
        # get数据
        response = await self.client.get("/admin/role/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["name"] == "John"
        # update
        pk = data["data"]["items"][0]["pk"]
        response = await self.client.get(f"/admin/role/update/{pk}")
        assert response.status_code == 200
        assert response.json()["status"] == 0
        role_data["name"] = "Amd"
        response = await self.client.put(f"/admin/role/update/{pk}", json=role_data)
        assert response.status_code == 200
        response = await self.client.get("/admin/role/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["name"] == "Amd"
