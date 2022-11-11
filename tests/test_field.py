"""
测试所有类型的字段的写入和读取
"""
from tests.base import BaseSite


class TestDecimalControl(BaseSite):
    async def test_dec(self):
        await self.login()
        response = await self.client.get("/admin/Dec/schema")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        # 测试写入数据
        role_data = {
            "dec1": 100,
        }
        response = await self.client.post("/admin/Dec/create", json=role_data)
        assert response.status_code == 200
        # get数据
        response = await self.client.get("/admin/Dec/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["dec1"] == 100
        self.assertEqual(data["data"]["items"][0]["dec2"], None)


class TestIntEnumControl(BaseSite):
    async def test_intenum(self):
        await self.login()
        response = await self.client.get("/admin/IntEnumField/schema")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        # 测试写入数据
        role_data = {"e2": "two"}
        response = await self.client.post("/admin/IntEnumField/create", json=role_data)
        assert response.status_code == 200
        data = response.json()
        self.assertEqual(data, None)
        # get数据
        response = await self.client.get("/admin/IntEnumField/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 0
        assert data["data"]["total"] == 1
        self.assertEqual(data["data"]["items"][0]["e1"], None)
        assert data["data"]["items"][0]["e2"] == "two"
        role_data = {"e2": "three"}
        response = await self.client.post("/admin/IntEnumField/create", json=role_data)
        assert response.status_code == 200
        data = response.json()
        self.assertEqual(data, {"status": 400, "msg": "e2 不能为 three", "data": {}})
