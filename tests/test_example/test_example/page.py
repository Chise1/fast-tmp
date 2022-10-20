"""
测试插件功能，支持自己写入规则
"""
from starlette.requests import Request

from fast_tmp.amis.forms import Control, Form
from fast_tmp.amis.page import Page
from fast_tmp.site.base import RegisterRouter


class MarkdownItem(Control):
    langeuage: str
    type = "editor"


class UserSelfInfo(RegisterRouter):
    def __init__(self):
        super().__init__("info", "info")

    async def get_app_page(self, request: Request) -> dict:
        return Page(title="userselfinfo", body=[Form(
            name="form", body=[MarkdownItem(langeuage="markdown", name="markdown", label="markdown")],
            api="/form-test"
        )]).dict(exclude_none=True)
