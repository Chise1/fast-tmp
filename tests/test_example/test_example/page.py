"""
测试插件功能，支持自己写入规则
"""
from starlette.requests import Request

from fast_tmp.amis.formitem import FormItem
from fast_tmp.amis.forms import Form
from fast_tmp.amis.page import Page
from fast_tmp.site.base import PageRouter


class MarkdownItem(FormItem):
    langeuage: str
    type = "editor"


class UserSelfInfo(PageRouter):
    def __init__(self):
        super().__init__("info", "info")

    async def get_app_page(self, request: Request) -> Page:
        return Page(
            title="userselfinfo",
            body=[
                Form(
                    name="form",
                    body=[MarkdownItem(langeuage="markdown", name="markdown", label="markdown")],
                    api="/form-test",
                )
            ],
        )
