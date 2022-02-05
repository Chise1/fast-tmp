from fastapi.testclient import TestClient
from fastapi import FastAPI

from fast_tmp.admin.server import admin

app = FastAPI()
app.mount("/admin", admin, name="admin", )


def get_cookie(client: TestClient):
    login_post_res = client.post("/admin/login", data={"username": "root", "password": "root"})
    assert login_post_res.status_code == 307
    return login_post_res.cookies.get("access_token")


def test_sing_in():
    client = TestClient(app)
    login_res = client.get("/admin/login")
    assert login_res.status_code == 200
    assert login_res.text.count("<h2 class=\"card-title text-center mb-4\">Login to your account</h2>") == 1
    login_post_res = client.post("/admin/login", data={"username": "root", "password": "root"})
    assert login_post_res.status_code == 307
    assert login_post_res.headers.get("location") == 'http://testserver/admin/'


def test_site():
    client = TestClient(app)
    get_cookie(client)
    site_res = client.get("/admin/site")
    assert site_res.status_code == 200
    assert site_res.json() == {"status": 0, "msg": "", "data": {
        "pages": [{"label": "Auth", "children": [{"label": "User", "url": "User", "schemaApi": "User/schema"}]}]}}


def test_schema():
    client = TestClient(app)
    get_cookie(client)
    user_schema = client.get("/admin/User/schema")
    assert user_schema.status_code == 200
    assert user_schema.text == '{"status":0,"msg":"","data":{"type":"page","title":"User","body":[{"type":"button","label":"新增","actionType":"dialog","size":"md","level":"primary","dialog":{"title":"新增","nextCondition":true,"size":"md","body":{"type":"form","name":"新增User","title":"新增User","api":"post:/admin/User/create","body":[{"type":"input-text","name":"username","label":"username","inline":false,"submitOnChange":false,"disabled":false,"required":false,"validations":{"maxLength":128},"mode":"normal","size":"full"},{"type":"input-text","name":"password","label":"password","inline":false,"submitOnChange":false,"disabled":false,"required":false,"validations":{"maxLength":128},"mode":"normal","size":"full"}]}}},{"type":"crud","api":"User/list","columns":[{"type":"text","name":"id","label":"id"},{"type":"text","name":"username","label":"username"},{"type":"text","name":"is_active","label":"is_active"},{"buttons":[{"type":"button","label":"删除","actionType":"ajax","size":"md","level":"danger","confirmText":"确认要删除？","api":"delete:User/delete?id=$id"},{"type":"button","label":"修改","actionType":"dialog","size":"md","level":"primary","dialog":{"title":"修改","nextCondition":true,"size":"md","body":{"type":"form","name":"修改User","api":"put:User/update?id=$id","initApi":"get:User/update?id=$id","body":[{"type":"input-text","name":"password","label":"password","inline":false,"submitOnChange":false,"disabled":false,"required":false,"validations":{"maxLength":128},"mode":"normal","size":"full"}]}}}],"type":"operation","label":"操作"}],"affixHeader":false}],"initFetch":false}}'


def test_crud():
    client = TestClient(app)
    get_cookie(client)
    # create
    create_user = client.post("/admin/User/create", json={"username": "crud_user", "password": "crud_user"})
    assert create_user.status_code == 200
    assert create_user.text == '{"status":0,"msg":"","data":{"username":"crud_user","password":"crud_user"}}'
    # login
    login_post_res = client.post("/admin/login", data={"username": "crud_user", "password": "crud_user"})
    assert login_post_res.status_code == 307
    # list
    user_list = client.get("/admin/User/list")
    assert user_list.status_code == 200
    assert user_list.text == '{"status":0,"msg":"","data":{"items":[{"id":1,"username":"root","is_active":true},{"id":2,"username":"crud_user","is_active":true}],"total":2}}'
