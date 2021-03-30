import asyncio
import importlib
import os
import typer

app = typer.Typer()
try:
    from fast_tmp.conf import settings

    settings.script_app = app
except Exception as e:
    print(f"warning:{e}")
    settings = None


@app.command()
def createsuperuser(username: str, password: str):
    """
    创建超级用户
    """

    async def create_superuser(username: str, password: str):
        from fast_tmp.models import User
        await User.create(username=username, password=password, is_superuser=True)

    asyncio.run(create_superuser(username, password))
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
if settings:
    for i in settings.EXTRA_SCRIPT:
        mod = importlib.import_module(i)


def main():
    app()


if __name__ == "__main__":
    main()
