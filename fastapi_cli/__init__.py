import datetime
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


@app.command()
def createsuperuser(username: str, password: str):
    """
    创建超级用户
    """
    import os
    project_slug = os.path.split(os.getcwd())[1]
    os.environ.setdefault('FASTAPI_SETTINGS_MODULE', project_slug + ".settings")
    from fast_tmp.models import User
    from fast_tmp.db import engine
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        user = User(
            username=username, is_superuser=True)
        user.set_password(password)
        session.add(user)
        session.commit()
    print(f"创建{username}成功")


@app.command()
def downlocalstatic():# todo need finish
    """
    下载amis所需的静态文件(未完成)
    """
    pass


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
if settings and settings.EXTRA_SETTINGS.get("EXTRA_SCRIPT"):
    for i in settings.EXTRA_SETTINGS.get("EXTRA_SCRIPT"):
        path_list = i.split(".")
        mod = importlib.import_module(".".join(path_list[0:-1]))
        for k, v in mod.__dict__.items():
            if k == path_list[-1]:
                app.command()(v)


@app.command()
def access_token(username: str):
    """
    创建一个测试token
    """
    from fast_tmp.utils.token import create_access_token

    print(create_access_token(
        data={"sub": username},
        expires_delta=datetime.timedelta(
            hours=30
        )
    ))


def main():
    app()


if __name__ == "__main__":
    main()
