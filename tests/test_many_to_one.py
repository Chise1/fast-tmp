from fastapi import FastAPI
from fastapi.testclient import TestClient

from fast_tmp.admin.server import admin
from fast_tmp.db import get_db_session

from .models import Author, Book

app = FastAPI()
app.mount("/admin", admin, name="admin")


def get_cookie(client: TestClient):
    login_post_res = client.post("/admin/login", data={"username": "root", "password": "root"})
    assert login_post_res.status_code == 307
    return login_post_res.cookies.get("access_token")


def write_base_data():
    session_c = get_db_session()
    session = next(session_c)

    next(session_c)
