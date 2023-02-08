# admin详细入门教程

## 创建项目

创建一个文件夹```fast-tmp-study```

```shell
mkdir fast-tmp-study
```

创建虚拟环境（以poetry为例）

```shell
poetry init
poetry install
```

修改软件源（一般情况下不用修改，现在国内用默认源挺快的）,
修改`pyproject.toml`文件，在后面加上：

```toml
[[tool.poetry.source]]
url = "https://mirrors.aliyun.com/pypi/simple/" # 如果是其他源自己改
name = "aliyun"
default = true
```

安装fast-tmp（注意，fast-tmp最低支持python3.8）

```shell
poetry add fast-tmp
```

安装`cookiecutter`，这个包只有在创建项目的时候才用上，所以用pip安装

```shell
pip3 install cookiecutter
```

通过fast-tmp创建项目模板

```shell
fast-tmp startproject
```

然后需要创建数据表，如果使用aerich则请参考aerich官网进行创建。
如果想简单点，可以修改src/app.py文件下的配置为：

```pycon
register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=True) # generate_schemas配置为true会自动创建数据表
```

并进入src文件夹，启动一次app.py文件。（如何配置python解释器为poetry创建的解释器就不赘述了）
然后在src文件夹下执行(注意需要使用poetry的虚拟环境):

```shell
fast-tmp creatersuperuser admin admin
```

即可创建管理员。
访问http://127.0.0.1:8000/admin/login页面可登录并进入后台管理。
![登录页面](./images/登录页面.png)
![主页](./images/主页.jpg)

## 注册模型

将一个模型生成一个管理页面的标准流程：

1. 编写对应的admin类
2. 注册到admin服务上去。

### 示例

假设我们有一个author，一个book表，修改fast_tmp_example/models.py文件如下：

```python
from tortoise import fields
from tortoise.models import Model
from fast_tmp.contrib.tortoise.fields import ImageField # fast-tmp自己的字符


class Author(Model):
    name = fields.CharField(max_length=255, description="名字")
    birthday = fields.DateField(description="生日")
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name


class Book(Model):
    name = fields.CharField(max_length=255, description="书名")
    author: fields.ForeignKeyRelation[Author] = fields.ForeignKeyField(
        "fast_tmp.Author", related_name="books", description="作者"
    )
    cover = ImageField(description="封面")
    rating = fields.FloatField(description="价格")
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

```

创建对应的admin类，修改fast_tmp_example/admin.py如下：
```python
from fast_tmp.site import ModelAdmin
from fast_tmp_example.models import Book, Author


class BookModel(ModelAdmin):
    model = Book
    list_display = ("name", "author", "rating", "cover") # list列表显示的字段
    create_fields = ("name", "author", "rating", "cover")# 创建页面的字段
    update_fields = ("name", "author", "cover")# 更新字段
    filters = ("name__contains",) # 过滤字段
    ordering = ("author",)# 排序字段


class AuthorModel(ModelAdmin):
    model = Author
    list_display = ("name", "birthday")
    create_fields = ("name", "birthday")
    update_fields = ("name", "birthday")
    ordering = ("name",)

```
修改app.py文件，增加注册行：
```python
from tortoise.contrib.fastapi import register_tortoise
from fast_tmp.conf import settings
from fast_tmp.admin.register import register_static_service
from fast_tmp.site import register_model_site
from fast_tmp.factory import create_app
from fast_tmp_example.admin import AuthorModel, BookModel

app = create_app()
app.title = "fast_tmp_example"

register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=True)
if settings.DEBUG:
    register_static_service(app)
register_model_site({"date": [AuthorModel(), BookModel()]}) # 这一行是增加的，date是分组名称

if __name__ == "__main__":
    import uvicorn  # type:ignore

    uvicorn.run(app, port=8000, lifespan="on")

```
安装aiofiles（文件类型字段必须使用的包）

最后效果如下：
![author1](./images/page/author1.png)
![author_create](./images/page/author_create.png)
![author2](./images/page/author2.png)
![book_create](./images/page/book_create.png)
![book1](./images/page/book1.png)
