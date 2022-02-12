from fastapi import FastAPI
from fastapi.testclient import TestClient

from fast_tmp.admin.server import admin

app = FastAPI()
app.mount(
    "/admin",
    admin,
    name="admin",
)


def get_cookie(client: TestClient):
    login_post_res = client.post("/admin/login", data={"username": "root", "password": "root"})
    assert login_post_res.status_code == 307
    return login_post_res.cookies.get("access_token")


def test_sing_in():
    client = TestClient(app)
    login_res = client.get("/admin/login")
    assert login_res.status_code == 200
    assert (
        login_res.text.count('<h2 class="card-title text-center mb-4">Login to your account</h2>')
        == 1
    )
    login_post_res = client.post("/admin/login", data={"password": "root1"})
    assert login_post_res.status_code == 200
    assert login_post_res.text.count("Username can not be null.") == 1
    login_post_res = client.post("/admin/login", data={"username": "root1"})
    assert login_post_res.status_code == 200
    assert login_post_res.text.count("Password can not be null.") == 1

    login_post_res = client.post("/admin/login", data={"username": "root1", "password": "sadf"})
    assert login_post_res.status_code == 200
    assert login_post_res.text.count("Username or password is error!") == 1

    login_post_res = client.post("/admin/login", data={"username": "root", "password": "root"})
    assert login_post_res.status_code == 307
    assert login_post_res.headers.get("location") == "http://testserver/admin/"
    # sign out
    assert (
        client.get("/admin/logout").text.count(
            '<h2 class="card-title text-center mb-4">Login to your account</h2>'
        )
        == 1
    )


def test_site():
    client = TestClient(app)
    get_cookie(client)
    site_res = client.get("/admin/site")
    assert site_res.status_code == 200
    assert site_res.json() == {
        "data": {
            "pages": [
                {
                    "children": [
                        {"label": "User", "schemaApi": "endpoint/User/schema", "url": "User"},
                        {"label": "Group", "schemaApi": "endpoint/Group/schema", "url": "Group"},
                    ],
                    "label": "Auth",
                }
            ]
        },
        "msg": "",
        "status": 0,
    }


def test_schema():
    client = TestClient(app)
    get_cookie(client)
    user_schema = client.get("/admin/endpoint/User/schema")
    assert user_schema.status_code == 200
    assert (
        user_schema.text
        == '{"status":0,"msg":"","data":{"type":"page","title":"User","body":[{"type":"button","label":"新增","actionType":"dialog","size":"md","level":"primary","dialog":{"title":"新增","nextCondition":true,"size":"md","body":{"type":"form","name":"新增User","title":"新增User","api":"post:endpoint/User/create","body":[{"type":"input-text","name":"username","label":"username","inline":false,"submitOnChange":false,"disabled":false,"required":false,"validations":{"maxLength":128},"mode":"normal","size":"full"},{"type":"input-text","name":"password","label":"password","inline":false,"submitOnChange":false,"disabled":false,"required":false,"validations":{"maxLength":128},"mode":"normal","size":"full"}]}}},{"type":"crud","api":"endpoint/User/list","columns":[{"type":"text","name":"id","label":"id"},{"type":"text","name":"username","label":"username"},{"type":"text","name":"is_active","label":"is_active"},{"buttons":[{"type":"button","label":"删除","actionType":"ajax","size":"md","level":"danger","confirmText":"确认要删除？","api":"delete:endpoint/User/delete?id=$id"},{"type":"button","label":"修改","actionType":"dialog","size":"md","level":"primary","dialog":{"title":"修改","nextCondition":true,"size":"md","body":{"type":"form","name":"修改User","api":"put:endpoint/User/update?id=$id","initApi":"get:endpoint/User/update?id=$id","body":[{"type":"input-text","name":"password","label":"password","inline":false,"submitOnChange":false,"disabled":false,"required":false,"validations":{"maxLength":128},"mode":"normal","size":"full"}]}}}],"type":"operation","label":"操作"}],"affixHeader":false}],"initFetch":false}}'
    )


def test_crud():
    client = TestClient(app)
    get_cookie(client)
    assert client.get("/admin/").text.count("<title>amis admin</title>")
    assert client.post("/admin/").text.count("<title>amis admin</title>")
    # create
    create_user = client.post(
        "/admin/endpoint/User/create", json={"username": "crud_user", "password": "crud_user"}
    )
    assert create_user.status_code == 200
    assert (
        create_user.text
        == '{"status":0,"msg":"","data":{"username":"crud_user","password":"crud_user"}}'
    )
    # login
    login_post_res = client.post(
        "/admin/login", data={"username": "crud_user", "password": "crud_user"}
    )
    assert login_post_res.status_code == 307
    assert login_post_res.next.path_url == "/admin/"
    # list
    user_list = client.get("/admin/endpoint/User/list")
    assert user_list.status_code == 200
    assert user_list.text.count('"username":"crud_user"') == 1
    user_data = user_list.json()["data"]
    assert user_data["total"] == 2
    for i in user_data["items"]:
        if i.get("username") == "crud_user":
            user_id = i.get("id")
            break
    else:
        raise Exception("not found user id")
    # update
    user_update = client.get(f"/admin/endpoint/User/update?id={user_id}")
    assert user_update.status_code == 200
    assert user_update.text.count('"password":') == 1
    user_update_p = client.put(
        f"/admin/endpoint/User/update?id={user_id}", json={"password": "root"}
    )
    assert user_update_p.status_code == 200
    assert user_update_p.json()["status"] == 0
    # test error pk
    user_delete_err = client.delete(f"/admin/endpoint/User/delete?ids={user_id}")
    error_data = user_delete_err.json()
    assert error_data["status"] == 400
    assert error_data["msg"] == "主键错误"
    error_data = client.put(
        f"/admin/endpoint/User/update?ids={user_id}", json={"password": "root"}
    ).json()
    assert error_data["status"] == 400
    assert error_data["msg"] == "主键错误"
    # delete
    user_delete = client.delete(f"/admin/endpoint/User/delete?id={user_id}")
    assert user_delete.status_code == 200


def test_not_singin():
    client = TestClient(app)
    assert client.get("/admin/endpoint/User/list").text.count("Login to your account") == 1
    assert (
        client.post(
            "/admin/endpoint/User/create", json={"username": "crud_user1", "password": "tt"}
        ).status_code
        == 307
    )
    assert client.get("/admin/endpoint/User/update?id=1").text.count("Login to your account") == 1
    assert (
        client.put("/admin/endpoint/User/update?id=1", json={"password": "asdfadf"}).status_code
        == 307
    )
    assert client.delete("/admin/endpoint/User/delete?id=1").status_code == 307
    assert client.get("/admin/endpoint/User/schema").text.count("Login to your account") == 1
    assert client.get("/admin/site").text.count("Login to your account") == 1
    assert client.get("/admin/").text.count("Login to your account") == 1
    assert client.post("/admin/").status_code == 307


def test_local_static():
    client = TestClient(app)
    get_cookie(client)
    assert (
        client.get("/admin/").text.count(
            '<script src="https://unpkg.com/amis@beta/sdk/sdk.js"></script>'
        )
        == 1
    )
