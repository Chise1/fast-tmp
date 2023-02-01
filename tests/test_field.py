"""
测试所有类型的字段的写入和读取
"""
from tests.base import BaseSite


class TestDecimalControl(BaseSite):
    async def test_dec(self):
        await self.login()
        response = await self.client.get("/admin/dec/schema")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        # 测试写入数据
        role_data = {
            "dec1": 100,
        }
        response = await self.client.post("/admin/dec/create", json=role_data)
        assert response.status_code == 200
        # get数据
        response = await self.client.get("/admin/dec/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["dec1"] == 100
        self.assertEqual(data["data"]["items"][0]["dec2"], None)


class TestIntEnumControl(BaseSite):
    async def test_intenum(self):
        await self.login()
        response = await self.client.get("/admin/intenumfield/schema")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        # 测试写入数据
        role_data = {"int_enum_2": "two", "bool_2": "False"}
        response = await self.client.post("/admin/intenumfield/create", json=role_data)
        assert response.status_code == 200
        data = response.json()
        self.assertEqual(data, None)
        # get数据
        response = await self.client.get("/admin/intenumfield/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        assert data["data"]["total"] == 1
        self.assertEqual(data["data"]["items"][0]["int_enum_1"], None)
        assert data["data"]["items"][0]["int_enum_2"] == "two"
        assert data["data"]["items"][0]["bool_2"] == "False"
        assert data["data"]["items"][0]["bool_1"] == "None"
        role_data = {"int_enum_2": "three", "bool_1": "xx"}
        response = await self.client.post("/admin/intenumfield/create", json=role_data)
        assert response.status_code == 200
        data = response.json()
        self.assertEqual({"data": {}, "msg": "one: 1\ntwo: 2 不能为 three", "status": 400}, data)
