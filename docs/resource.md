# 参考
## 模型

### 页面模型
**PageRouter**

通过继承```PageRouter```可以创建一个能够注册到admin管理平台的页面。
```python
class PageRouter:
    """
    页面基类，用于提供注册到admin管理页面的抽象类。
    
    """

    async def get_app_page(self, request: Request) -> Page:
        """
        继承该类并实现该接口,返回一个Page实例
        该接口会被fast_tmp.admin.endpoint里面的```/{resource}/schema```接口调用
        其中resource参数即为prefix
        """

    def __init__(self, prefix: str, name: str):
        """
        注册到admin的页面会生成对应页面权限，权限codename为{prefix}_create、{prefix}_update、{prefix}_delete、{prefix}_list

        name: 导航栏名字
        prefix: 为接口的resource
        """


    async def router(self, request: Request, resource: str, method: str) -> BaseRes:
        """
        用于自定义接口的方法
        当自定义该接口之后，会被fast_tmp.admin.endpoint里面的```/{prefix}/extra/{resource}```接口调用
        支持的method为["POST", "GET", "DELETE", "PUT", "PATCH"]
        resource: str
        method: str "POST", "GET", "DELETE", "PUT", "PATCH" 中的一个
        """


    def get_create_controls(self, request: Request, codenames: Iterable[str]) -> Iterable[FormItem]:
        """
        当外键或多对多创建的时候，子表的创建字段由此返回
        如果没有可以不编写该函数
        """
```
一个最简单的示例，增加一个helloworld页面。
```python
class HelloWorldPage(PageRouter):
    async def get_app_page(self, request: Request) -> Page:
        """
        继承该类并实现该接口,返回一个Page实例
        该接口会被fast_tmp.admin.endpoint里面的```/{resource}/schema```接口调用
        其中resource参数即为prefix
        """
        return Page(
            body=[Tpl(tpl="Hello World")]
        )
```
然后通过register_model_site注册：
```python
register_model_site(
{"Hello": [HelloWorldPage(name="Hello",prefix="prefix")]}
)
```
### 数据表模型
通过```ModelAdmin```将数据表映射为页面操作。
该类参考了django对应功能的实现。
```python
class ModelAdmin(ModelSession, PageRouter):
    model: Type[Model]  # model
    list_display: Tuple[str, ...] = ()  # 页面展示的字段
    inline: Tuple[str, ...] = ()  # 可在页面直接修改的字段
    # search list
    filters: Tuple[Union[str, ModelFilter], ...] = ()  # 过滤字段的字典，字段名和对应的ModelFilter
    ordering: Tuple[str, ...] = ()  # 定义哪些字段支持排序
    # create
    create_fields: Tuple[str, ...] = ()  # 创建页面的字段
    update_fields: Tuple[str, ...] = ()  # 更新页面的字段
    fields: Dict[str, BaseAdminControl] = None  # 如果有自定义页面字段，在这里加入。 type: ignore
    methods: Tuple[str, ...] = (  # 页面功能，如果不想有创建或者更新或者删除，可以删除里面的字段。
        "list","create","put","delete")
```
示例：
```python
# 假设有两个模型：

class Author(Model):
    """
    作者
    """
    name = fields.CharField(max_length=255, description="名字")
    birthday = fields.DateField(description="生日")
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name


class Book(Model):
    """
    书籍
    """
    name = fields.CharField(max_length=255, description="书名")
    author: fields.ForeignKeyRelation[Author] = fields.ForeignKeyField(
        "fast_tmp.Author", related_name="books", description="作者"
    )
    cover = ImageField(description="封面")
    rating = fields.FloatField(description="价格")
    quantity = fields.IntField(default=0, description="存量")
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name


# 可以生成如下：


class BookModel(ModelAdmin):
    model = Book
    list_display = ("name", "author", "rating", "cover")
    create_fields = ("name", "author", "rating", "cover")
    update_fields = ("name", "author", "cover")
    filters = ("name__contains",)
    ordering = ("author",)


class AuthorModel(ModelAdmin):
    model = Author
    list_display = ("name", "birthday")
    inline = ("name",)
    create_fields = ("name", "birthday")
    update_fields = ("name", "birthday")
    ordering = ("name",)

```
## 字段
## 参考
## 杂项
### 前后端数据一致性
tortoise-orm和amis页面数据格式并不完全一致，需要进行转换工作，主要依靠继承的```AmisOrm```类完成：
```python
class AmisOrm:
    """
    orm和amis之间的数据转换
    """
    def orm_2_amis(self, value: Any) -> Any:
        """
        orm的值转成amis需要的值
        """

    def amis_2_orm(self, value: Any) -> Any:
        """
        amis数据转orm
        """
```