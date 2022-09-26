import importlib
import os
import typer
import sys
from asgiref.sync import async_to_sync

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


@async_to_sync
async def create_superuser(username: str, password: str):
    from tortoise import Tortoise
    await Tortoise.init(config=settings.TORTOISE_ORM)
    from fast_tmp.models import User
    if User.filter(username=username).exists():
        print(f"{username} 已经存在了")
        exit(1)
    user = User(username=username, is_superuser=True)
    user.set_password(password)
    await user.save()
    sys.stdout.write(f"创建{username}成功")


@async_to_sync
async def make_permissions():
    from tortoise import Tortoise
    from fast_tmp.utils.model import get_all_models
    from fast_tmp.models import Permission
    await Tortoise.init(config=settings.TORTOISE_ORM)
    all_model = get_all_models()
    for model in all_model:
        model_name=model.__name__.lower()
        await Permission.get_or_create(codename=model_name + "_create", defaults={"label": f"{model_name}__创建"})
        await Permission.get_or_create(codename=model_name + "_update", defaults={"label": f"{model_name}__更新"})
        await Permission.get_or_create(codename=model_name + "_delete", defaults={"label": f"{model_name}__删除"})
        await Permission.get_or_create(codename=model_name + "_list", defaults={"label": f"{model_name}__修改"})
    sys.stdout.write("构建权限表完成")


@app.command()
def make_perm():
    """
    同步所有model的权限
    """
    make_permissions()


@app.command()
def createsuperuser(username: str, password: str):
    """
    创建超级用户
    """
    create_superuser(username, password)


@app.command()
def startproject():
    """
    创建项目
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    from cookiecutter.main import cookiecutter
    print(basedir)
    cookiecutter(os.path.join(basedir,"tpl/project"))

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


def main():
    app()


if __name__ == "__main__":
    main()
