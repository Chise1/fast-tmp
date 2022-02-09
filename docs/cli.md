# fast-tmp脚本指令说明

## createsupuser

创建一个超级用户，用法如下:

```shell
fast-tmp createsuperuser username password
```

## 初始化一个项目

通过自定义的模板进行，需要安装cookiecutter，或者在安装fast-tmp的时候执行```pip install fast-tmp[cli]```

然后可以执行```fast-tmp startproject```即可创建一个项目的基本结构。

## 自定义脚本

在settings.py里面引入自定义脚本所在的路径，即可自动读取并注册到脚本里面去， 例如：

```python
# cli.py
def hello():
    """
    你好.
    """
    print("hello world.")


# settings.py
EXTRA_SCRIPT = ['cli.hello']  # 自定义执行脚本

```

然后执行```fast-tmp```即可查看到自己注册的方法。
