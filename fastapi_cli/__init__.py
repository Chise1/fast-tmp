import asyncio
import importlib
import os
import typer
import sys

app = typer.Typer()
for path in sys.path:
    if path == os.getcwd():
        break
else:
    sys.path.append(os.getcwd())
try:
    from fast_tmp.conf import settings
except Exception as e:
    print(f"warning:{e}")
    settings = None


async def create_superuser(username: str, password: str):
    from tortoise import Tortoise
    await Tortoise.init(config=settings.TORTOISE_ORM)
    from fast_tmp.models import User
    user = User(username=username, is_superuser=True)
    user.set_password(password)
    await user.save()


@app.command()
def createsuperuser(username: str, password: str):
    """
    创建超级用户
    """

    asyncio.run(create_superuser(username, password))
    print(f"创建{username}成功")


@app.command()
def startapp():
    """
    创建app
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    cookiecutter(basedir + "/tpl/app/")


@app.command()
def startproject():
    """
    创建项目
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    cookiecutter(basedir + "/tpl/project")


@app.command()
def staticfile():
    """
    离线环境下的swagger静态文件
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    cookiecutter(basedir + "/tpl/static")


# 导入自定义脚本执行方式
if settings:
    if settings.EXTRA_SETTINGS.get("EXTRA_SCRIPT"):
        for i in settings.EXTRA_SETTINGS.get("EXTRA_SCRIPT"):
            mod = importlib.import_module(i)


def main():
    app()


if __name__ == "__main__":
    main()
