"""
测试自定义脚本
"""
import asyncio

from .models import Author


async def _create_author(name: str):
    await Author.create(name=name)


def create_author(name: str):
    """
    创建新作者
    """
    asyncio.run(_create_author(name))
