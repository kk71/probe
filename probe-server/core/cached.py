# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseCached"
]

import asyncio
from typing import Any, Callable


class BaseCached:
    """基础缓存"""

    # 数据过期时间
    EXPIRE_TIME = 60

    # 数据
    # TODO 务必重载
    CACHED_DATA: Any = None

    # 日志方法
    LOGGER_METHOD: Callable = None

    @classmethod
    def content_on_update(cls, *args, **kwargs):
        """缓存的数据需要更新的时候的回调"""
        raise NotImplementedError

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        """缓存的数据初始化"""
        raise NotImplementedError

    @classmethod
    def initialized(cls) -> bool:
        """当前缓存数据是否已经初始化"""
        return True if cls.CACHED_DATA is not None else False

    @classmethod
    async def start(cls, *args, **kwargs):
        while True:
            r = cls.content_initialize(*args, **kwargs)
            if asyncio.iscoroutine(r):
                await r
            cls.LOGGER_METHOD(f"cached data {cls} is updated")
            await asyncio.sleep(cls.EXPIRE_TIME)
