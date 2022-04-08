# Author: kk.Fang(fkfkbill@gmail.com)

from .base import *
from utils import const


class ServiceUnavailable(SysNotification):
    """系统服务不可用"""

    LEVEL = const.SYSTEM_NOTIFICATION_LEVEL_ERROR


class CachedDataUpdatingFailed(SysNotification):
    """缓存数据更新失败"""

    LEVEL = const.SYSTEM_NOTIFICATION_LEVEL_ERROR
