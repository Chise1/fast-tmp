import jinja2
from pydantic import typing


def register_tags(templates):
    env = templates.env

    @jinja2.pass_context
    def static(context: dict, **path_params: typing.Any) -> str:
        request = context["request"]
        path = "admin"
        return request.url_for(path, **path_params)

    env.globals["static"] = static
