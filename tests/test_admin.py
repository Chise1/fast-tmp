from .base import BaseSite


class TestSite(BaseSite):
    async def test_login(self):
        response = await self.client.get("/admin/site")
        assert response.status_code == 302
        assert response.headers.get("location") == "http://test/admin/login"
        # 登录
        await self.login()
