# admin 页面

fast-tmp的页面主要是通过继承```PageRouter```类来实现，
```python
class PageRouter:
    """
    页面基类，用于提供注册到admin管理页面的抽象类
    """

    _name: str
    _prefix: str

    @abstractmethod
    async def get_app_page(self, request: Request) -> Page:
        """
        继承该类并实现该接口,返回一个Page实例
        该接口会被fast_tmp.admin.endpoint里面的```/{resource}/schema```接口调用
        其中resource参数即为prefix
        """

    def __init__(self, prefix: str, name: str):
        """
        name为左侧导航栏名字，prefix为接口的resource
        """
        self._name = name
        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix

    @property
    def name(self) -> str:
        return self._name

    async def router(self, request: Request, prefix: str, method: str) -> BaseRes:
        """
        用于自定义接口的方法
        当自定义该接口之后，会被fast_tmp.admin.endpoint里面的```/{resource}/extra/{prefix}```接口调用
        支持的method为["POST", "GET", "DELETE", "PUT", "PATCH"]
        """
        raise NotFoundError("not found function.")
```
## 注册到页面

注册页面的方式很简单，只需要继承该类并实现，然后通过注册接口注册即可：
一个简单的自定义页面(展示用户自己的个人信息)
```python

class UserSelfInfo(PageRouter):
    def __init__(self):
        super().__init__("info", "info")

    async def get_app_page(self, request: Request) -> Page:
        return Page(
            title="userselfinfo",
            body=[
                Form(
                    name="form",
                    body=[MarkdownItem(langeuage="markdown", name="markdown", label="markdown")],
                    api="/form-test",
                )
            ]
        )
```

在main函数所在的页面进行注册：
```python
register_model_site(# fieldtesting为左侧导航的一级名称
    {"fieldtesting": [..., UserSelfInfo()]}
)
```
即可在页面左侧展示


