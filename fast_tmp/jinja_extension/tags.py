import os.path

import jinja2
from pydantic import typing

from fast_tmp.conf import settings


def register_tags(templates):
    env = templates.env

    @jinja2.pass_context
    def static(context: dict, **path_params: typing.Any) -> str:
        return "/" + os.path.join(settings.STATIC_PATH, path_params["path"])

    env.globals["static"] = static

    # 是否使用本地静态文件

    @jinja2.pass_context
    def local_file(
        context: dict,
    ) -> bool:
        return settings.LOCAL_FILE

    env.globals["local_file"] = local_file
