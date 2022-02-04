[![Python package](https://github.com/Chise1/fast-tmp/actions/workflows/python-package.yml/badge.svg)](https://github.com/Chise1/fast-tmp/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/Chise1/fast-tmp/branch/main/graph/badge.svg?token=7CZE532R0H)](https://codecov.io/gh/Chise1/fast-tmp)

# fast-tmp

项目模板

## task

1. 支持常见的字段类型
2. 完善单元测试
3. 完善文档
4. 支持枚举类型的显示和选择
5. 支持多对多关系
6. 支持外键关系
7. 支持i18n，并清理代码中的中文注释

## 概述

本项目主要是方便快速构建fastapi的后端开发环境，依赖于```cookiecutter```，并提供方便快捷的生成路由的方法。 主要使用的开发包：

1. fastapi
2. sqlalchemy

前端依赖的文件在项目的 /admin/static/amis内，自行解压缩

整个项目在开发过程中参考了django的一些实现方式，尽量做到简洁明了。

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

创建超级用户需要使用了fast-tmp自带的models， 首先，在项目.settings的TORTOISE_ORM里面配置fast-tmp的model

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

### crud生成器

crud生成器可以对大部分crud自动化生成（不包括文件或二进制流）。

crud一共有三个版本，目前最常用的是```utils.crud2```，crud3是类似于django的基于类的视图，但是个人感觉不灵活，目前用的不多。

crud1是以前的版本，现在不怎么用了，0.3.0之前会删掉。 具体的使用方法下次在写。。。
