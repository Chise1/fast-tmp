![PyPI](https://img.shields.io/pypi/v/fast-tmp?color=gree)
[![Python package](https://github.com/Chise1/fast-tmp/actions/workflows/python-package.yml/badge.svg)](https://github.com/Chise1/fast-tmp/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/Chise1/fast-tmp/branch/main/graph/badge.svg?token=7CZE532R0H)](https://codecov.io/gh/Chise1/fast-tmp)
[![Documentation Status](https://readthedocs.org/projects/fast-tmp/badge/?version=latest)](https://fast-tmp.readthedocs.io/?badge=latest)
![GitHub](https://img.shields.io/github/license/Chise1/fast-tmp)

# fast-tmp

## 概述

fast-tmp项目是基于fastapi+tortoise-orm而构建的后台管理系统，类似于django-admin。
依赖于amis低代码平台，后台可以很方便的通过json构建前台页面。
主要支持如下功能：

1. 完善的后台管理页面
2. 方便的脚本支撑功能

整个项目在开发过程中参考了django的一些实现方式。

## 演示

由于笔者比较穷租不起服务器给你们演示，所以你们可以自己拉个容器启动即可

## 安装fast-tmp

使用pip

```shell script
pip3 install fast-tmp
```

使用poetry

```shell script
poetry add fast-tmp
```

## 项目指令

目前包含的操作指令有两个:

1. 创建项目
2. 创建超级用户

支持自定义指令并创建

### 创建项目

```shell script
fast-tmp startproject
```

输入完所需的参数之后，就可以生成一个自己的项目。

### 创建超级用户

创建超级用户需要使用了fast-tmp自带的models，
首先，在项目.settings的TORTOISE_ORM里面配置fast-tmp的model

```python
import os

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'host': os.getenv("DB_HOST"),
                'port': os.getenv("DB_PORT"),
                'user': os.getenv("DB_USER"),
                'password': os.getenv("DB_PASSWORD"),
                'database': os.getenv("DB_NAME"),
            }
        },
    },
    'apps': {
        'fast_tmp': {
            'models': ['fast_tmp.models', 'aerich.models'],  # 注册app.models
            'default_connection': 'default',
        }
    }
}
```

然后，只需要执行：

```shell script
fast-tmp createsuperuser
```

### 自定义指令

在settings里面配置```EXTRA_SCRIPT```参数，就像配置django的参数一样，把脚本的相对导入路径写到这个字段列表里面，即可通过fast-tmp进行执行。

可以通过```fast-tmp --help```查看当前有哪些执行指令

## 功能

初始化项目之后，fast-tmp包里面有如下功能：

1. 全局settings管理
2. crud生成器

### 全局settings管理

这个主要功能就是在所有地方都是通过```fast_tmp.conf.settings```获取设置值或环境变量。

具体使用如下：

```python
from fast_tmp.conf import settings

...
```

## 配置文件路径[biz-perl0131.log](..%2F..%2F..%2FDownloads%2Fbiz-perl0131.log)

fast-tmp可以通过读取pyproject.toml文件获取到settings.py文件所在位置
只需要在pyproject.toml有这个配置：

```toml
[tool.fast-tmp]
tortoise_orm = "settings.TORTOISE_ORM"
```

或者使用aerich初始化过数据库，并在配置文件里有

```toml
[tool.aerich]
tortoise_orm = "settings.TORTOISE_ORM"
```
