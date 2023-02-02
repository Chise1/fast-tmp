"""
测试所有类型的字段的写入和读取
"""
import datetime

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
        role_data = {
            "int_enum_2": "two",
            "bool_2": "False",
            "datetime_4": datetime.datetime.fromtimestamp(0).strftime("%Y-%m-%d %H:%M:%S"),
            "datetime_3": datetime.datetime.fromtimestamp(0).strftime("%Y-%m-%d %H:%M:%S"),
        }
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
        assert data["data"]["items"][0]["bool_1"] is None
        assert data["data"]["items"][0]["datetime_1"] is None
        assert data["data"]["items"][0]["datetime_3"] == datetime.datetime.fromtimestamp(
            0
        ).strftime("%Y-%m-%d %H:%M:%S")
        assert data["data"]["items"][0]["datetime_4"] == datetime.datetime.fromtimestamp(
            0
        ).strftime("%Y-%m-%d %H:%M:%S")
        assert datetime.datetime.strptime(
            data["data"]["items"][0]["datetime_2"], "%Y-%m-%d %H:%M:%S"
        )
        role_data = {
            "int_enum_2": "three",
            "bool_1": "xx",
            "datetime_3": datetime.datetime.fromtimestamp(0).strftime("%Y-%m-%d %H:%M:%S"),
        }
        response = await self.client.post("/admin/intenumfield/create", json=role_data)
        assert response.status_code == 200
        data = response.json()
        self.assertEqual(
            {
                "data": None,
                "errors": {
                    "bool_1": "bool_1 不能为 xx",
                    "bool_2": "bool_2 不能为 None",
                    "int_enum_2": "one: 1\ntwo: 2 不能为 three",
                    "datetime_4": "datetime_4 不能为 None",
                },
                "msg": "",
                "status": 422,
            },
            data,
        )
