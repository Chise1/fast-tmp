from .base import BaseSite


class TestSite(BaseSite):
    async def test_login(self):
        response = await self.client.get("/admin/login")
        assert response.text.find("Login to your account")
        response = await self.client.post("/admin/login", data={"password": "admin"})
        assert response.text.find("Username can not be null.")
        response = await self.client.post("/admin/login", data={"username": "admin"})
        assert response.text.find("Password can not be null.")
        response = await self.client.post(
            "/admin/login", data={"username": "admin", "password": "123"}
        )
        assert response.text.find("Username or password is error!")
        await self.login()
        response = await self.client.get("/admin/logout")
        assert response.text.find("Login to your account")
        response = await self.client.get("/admin/site")
        assert response.status_code == 302
        assert response.headers.get("location") == "http://test/admin/login"
        await self.login()

    async def test_html(self):
        response = await self.client.get("/")
        assert response.text.find("brandName: 'fast-tmp'")

    async def test_html_user(self):
        await self.login()
        user_html_schema = await self.client.get("/admin/User/schema")
        self.assertEqual(
            user_html_schema.text,
            '{"status":0,"msg":"","data":{"type":"page","title":"user","body":[{"type":"button","label":"新增","actionType":"dialog","size":"md","level":"primary","dialog":{"title":"新增","size":"md","body":{"type":"form","name":"新增user","title":"新增user","api":"post:User/create","body":[{"type":"input-text","name":"username","label":"username","required":true},{"type":"input-password","name":"password","label":"password"},{"type":"input-text","name":"name","label":"name","required":true},{"type":"transfer","name":"groups","label":"groups","source":"get:User/select/groups","searchable":false,"statistics":true,"sortable":false,"selectMode":"list"},{"type":"select","name":"is_active","label":"is_active","value":"True","required":true,"options":["True","False"]},{"type":"select","name":"is_superuser","label":"is_superuser","value":"False","required":true,"options":["True","False"]},{"type":"select","name":"is_staff","label":"is_staff","value":"False","required":true,"options":["True","False"]}]}}},{"type":"crud","api":"User/list","columns":[{"name":"name","label":"name"},{"name":"username","label":"username"},{"name":"is_active","label":"is_active","quickEdit":{"model":"inline","type":"select","saveImmediately":true,"options":["True","False"]}},{"name":"is_superuser","label":"is_superuser","quickEdit":{"model":"inline","type":"select","saveImmediately":true,"options":["True","False"]}},{"name":"is_staff","label":"is_staff","quickEdit":{"model":"inline","type":"select","saveImmediately":true,"options":["True","False"]}},{"type":"operation","name":"","label":"操作","buttons":[{"type":"button","label":"修改","actionType":"dialog","size":"md","level":"link","dialog":{"title":"修改","size":"md","body":{"type":"form","name":"修改user","title":"修改user","api":"put:User/update/$pk","initApi":"get:User/update/$pk","body":[{"type":"input-text","name":"username","label":"username","required":true},{"type":"input-password","name":"password","label":"password"},{"type":"input-text","name":"name","label":"name","required":true},{"type":"transfer","name":"groups","label":"groups","source":"get:User/select/groups","searchable":false,"statistics":true,"sortable":false,"selectMode":"list"},{"type":"select","name":"is_active","label":"is_active","value":"True","required":true,"options":["True","False"]},{"type":"select","name":"is_superuser","label":"is_superuser","value":"False","required":true,"options":["True","False"]},{"type":"select","name":"is_staff","label":"is_staff","value":"False","required":true,"options":["True","False"]}]}}},{"type":"button","label":"删除","actionType":"ajax","size":"md","level":"link","className":"text-danger","confirmText":"确认要删除？","api":"delete:User/delete/$pk"}]}],"affixHeader":false,"quickSaveItemApi":"User/patch/$pk","syncLocation":false}]}}',
        )
