# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "InitializedDevice"
]

import json
from typing import Dict

from device import *
from models.redis import RedisDevice
from utils import const
from .nats import *


class InitializedDevice(Device):
    """可拨测的拨测端"""

    NATS_HANDLER = SchedulerNATSHandler

    CACHED_DATA: Dict[
        str,  # client_id
        "InitializedDevice"  # {拨测端信息}
    ] = None

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        new_data = {}
        async for key in RedisDevice.async_redis_db_instance.scan_iter(match="*"):
            client_id: str = key.decode('utf-8')
            device_info: dict = json.loads(
                (await RedisDevice.async_redis_db_instance.get(client_id)).decode('utf-8')
            )
            a_device = cls(**device_info)
            if a_device.status == const.DEVICE_STATUS_ONLINE and a_device.enabled:
                # 仅使用在线并且已启用的拨测端
                new_data[client_id] = a_device
        cls.CACHED_DATA = new_data

    @classmethod
    def get(cls, client_id: str) -> "InitializedDevice":
        """查询某个拨测端"""
        return cls.CACHED_DATA.get(client_id)
