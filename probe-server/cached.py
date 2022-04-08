# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "Cached"
]

import sys_noti
from core.cached import *
from sys_noti.base import SysNotificationLoggerMixin
from utils.decorators import func_loop
from settings import Setting


class Cached(BaseCached, metaclass=SysNotificationLoggerMixin):
    """缓存的数据"""

    EXPIRE_TIME = Setting.DEFAULT_CACHED_EXPIRY_TIME

    @classmethod
    @func_loop
    async def start(cls, *args, **kwargs):
        cls.LOGGER_METHOD = cls.logger.info
        try:
            await super().start(*args, **kwargs)
        except:
            cls.notifier(sys_noti.CachedDataUpdatingFailed, target=cls)
