import asyncio
import importlib
import os
from tmp.conf import settings
import typer

app = typer.Typer()
settings.script_app = app


async def __create_superuser(username: str, password: str):
    pass


@app.command()
def createsuperuser(username: str, password: str):
    """
    创建超级用户
    """
    asyncio.run(__create_superuser(username, password))
    print(f"创建{username}成功")


@app.command()
def startapp():
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    cookiecutter(basedir + "/tpl/app/")


@app.command()
def startproject():
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    cookiecutter(basedir + "/tpl/project")


# 导入自定义脚本执行方式
for i in settings.EXTRA_SCRIPT:
    mod = importlib.import_module(i)


def main():
    app()


if __name__ == "__main__":
    main()
