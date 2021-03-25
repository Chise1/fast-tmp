import asyncio
import os

import typer

app = typer.Typer()


async def __create_superuser(username: str, password: str):
    pass


@app.command()
def createsuperuser(username: str, password: str):
    """
    创建超级用户
    """
    project_slug = os.path.split(os.getcwd())[1]
    os.environ.setdefault('FASTAPI_SETTINGS_MODULE', project_slug + ".settings")
    asyncio.run(__create_superuser(username, password))
    print(f"创建{username}成功")


@app.command()
def startapp():
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    cookiecutter(basedir + "/tpl/app/")


@app.command()
def start_project():
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    cookiecutter(basedir + "/tpl/project")


def main():
    app()


if __name__ == "__main__":
    main()
