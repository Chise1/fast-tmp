from fastapi.testclient import TestClient
from fastapi import FastAPI

from fast_tmp.admin.server import admin

app = FastAPI()
app.mount("/admin", admin, name="admin", )


def test_admin_user():
    client = TestClient(app)
    login_res = client.get("/admin/login")
    assert login_res.status_code == 200
    assert login_res.text.count("<h2 class=\"card-title text-center mb-4\">Login to your account</h2>") == 1
    login_post_res = client.post("/admin/login", data={"username": "root", "password": "root"})
    assert login_post_res.status_code == 307
    assert login_post_res.headers.get("location") == 'http://testserver/admin/'
