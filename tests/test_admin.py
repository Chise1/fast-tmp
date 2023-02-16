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
        user_html_schema = await self.client.get("/admin/user/schema")
        self.assertEqual(
            '{"status":0,"msg":"","data":{"type":"page","title":"用户","body":[{"type":"button","label":"新增",'
            '"actionType":"dialog","level":"primary","dialog":{"title":"新增","size":"md","body":{"type":"form",'
            '"name":"新增用户","title":"新增用户","api":"post:user/create","body":[{"type":"input-text","name":"username",'
            '"label":"用户名","required":true},{"type":"input-password","name":"password","label":"密码"},'
            '{"type":"input-text","name":"name","label":"名称","required":true},{"type":"transfer","name":"groups",'
            '"label":"groups","sortable":false,"source":"get:user/select/groups","searchable":false,'
            '"statistics":true,"selectMode":"list"},{"type":"select","name":"is_active","label":"活跃","value":"True",'
            '"description":"(False则账户无法使用)","required":true,"options":["True","False"]},{"type":"select",'
            '"name":"is_superuser","label":"超级管理员","value":"False","required":true,"options":["True","False"]},'
            '{"type":"select","name":"is_staff","label":"职员","value":"False","description":"(False则无法登录管理界面)",'
            '"required":true,"options":["True","False"]}]}}},{"type":"crud","api":"user/list","columns":[{'
            '"name":"id","label":"id","sortable":true},{"name":"name","label":"名称","sortable":true},'
            '{"name":"username","label":"用户名","sortable":true},{"name":"is_active","label":"活跃","quickEdit":{'
            '"model":"inline","type":"select","saveImmediately":true,"options":["True","False"]}},'
            '{"name":"is_superuser","label":"超级管理员","quickEdit":{"model":"inline","type":"select",'
            '"saveImmediately":true,"options":["True","False"]}},{"name":"is_staff","label":"职员","quickEdit":{'
            '"model":"inline","type":"select","saveImmediately":true,"options":["True","False"]}},'
            '{"type":"operation","name":"","label":"操作","buttons":[{"type":"button","label":"修改",'
            '"actionType":"dialog","level":"link","dialog":{"title":"修改","size":"md","body":{"type":"form",'
            '"name":"修改用户","title":"修改用户","api":"put:user/update/$pk","initApi":"get:user/update/$pk",'
            '"body":[{"type":"input-text","name":"username","label":"用户名","required":true},{"type":"input-password",'
            '"name":"password","label":"密码"},{"type":"input-text","name":"name","label":"名称","required":true},'
            '{"type":"transfer","name":"groups","label":"groups","sortable":false,"source":"get:user/select/groups",'
            '"searchable":false,"statistics":true,"selectMode":"list"},{"type":"select","name":"is_active",'
            '"label":"活跃","value":"True","description":"(False则账户无法使用)","required":true,"options":["True","False"]},'
            '{"type":"select","name":"is_superuser","label":"超级管理员","value":"False","required":true,"options":['
            '"True","False"]},{"type":"select","name":"is_staff","label":"职员","value":"False","description":"('
            'False则无法登录管理界面)","required":true,"options":["True","False"]}]}}},{"type":"button","label":"删除",'
            '"actionType":"ajax","level":"link","className":"text-danger","confirmText":"确认要删除？",'
            '"api":"delete:user/delete/$pk"}]}],"affixHeader":false,"quickSaveItemApi":"user/patch/$pk",'
            '"syncLocation":false}]}}',
            user_html_schema.text,
        )
