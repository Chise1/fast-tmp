![PyPI](https://img.shields.io/pypi/v/fast-tmp?color=gree)
[![Python package](https://github.com/Chise1/fast-tmp/actions/workflows/python-package.yml/badge.svg)](https://github.com/Chise1/fast-tmp/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/Chise1/fast-tmp/branch/main/graph/badge.svg?token=7CZE532R0H)](https://codecov.io/gh/Chise1/fast-tmp)
[![Documentation Status](https://readthedocs.org/projects/fast-tmp/badge/?version=latest)](https://fast-tmp.readthedocs.io/?badge=latest)
![GitHub](https://img.shields.io/github/license/Chise1/fast-tmp)

# fast-tmp

## 概述

fast-tmp项目是基于fastapi+tortoise-orm而构建的后台管理系统，类似于django-admin。
依赖amis低代码平台，后台可以很方便的通过json构建前台页面。
提供完善的后台管理功能和权限功能

整个项目在开发过程中参考了django的实现方式。

## 演示

由于笔者比较穷租不起服务器给你们演示，所以你们可以自己拉个容器启动即可。

演示方式：
通过docker拉镜像：

```shell
sudo docker run -p 8000:8000 chise123/fast-tmp-example:v1.0.2
```

然后访问```http://127.0.0.1:8000/admin``` 即可，
超级用户的账户密码为```admin/123456```

使用说明请参考![教程](fast-tmp.readthedocs.io/?badge=latest)的快速入门。