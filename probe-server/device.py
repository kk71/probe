# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "Device",
    "DevicePayload"
]

import json

from core.device import *
from core.task import TaskType
from utils.dt_utils import *
from cached import *
from sys_noti.base import SCCSysNotificationLoggerMixin
from models.redis import RedisDevicePayload


class Device(BaseProbeDevice, Cached, metaclass=SCCSysNotificationLoggerMixin):
    """设备"""

    def __init__(self, **kwargs):

        super(Device, self).__init__(**kwargs)

        # 负载信息，不会录入设备信息的redis库，而是录入负载库
        self.payload = DevicePayload(**kwargs.get("payload", {}))

        try:
            self.start_time: datetime = str_to_dt(self.start_time)
            self.end_time: datetime = str_to_dt(self.end_time)
        except arrow.parser.ParserError:
            self.logger.warning(
                f"start_time and(or) end_time are in bad format, use default instead.")
            self.start_time: datetime = datetime(2000, 1, 1, 1, 1, 1)
            self.end_time: datetime = datetime(2000, 1, 1, 1, 1, 1)

    @property
    def available_task_type(self):
        return self._available_task_type

    @available_task_type.setter
    def available_task_type(self, value):
        if not value:
            value = []
        self._available_task_type = tuple([TaskType(*i) for i in value])

    def serialize(self):
        return json.dumps(dt_to_str(self._serialize()), ensure_ascii=False, indent=4)


class DevicePayload:
    """拨测端的负载信息"""

    def __init__(self, **kwargs):

        self._to_serialize = []

        def kw(k, default=None):
            self._to_serialize.append(k)
            return kwargs.get(k, default)

        self.client_id: str = kw("client_id")

        # ========负载状态，数据来自拨测端上报 ========
        # 当前执行任务数
        self.current_capacity: float = kw("current_capacity")

        # 设定最大执行任务数
        self.max_capacity: float = kw("max_capacity")

        # 负载
        self.load_rate: float = kw("load_rate")

        # 结束率
        self.done_rate: float = kw("done_rate")

        # 失败率
        self.exception_rate: float = kw("exception_rate")

        # ======== 分数 ========
        # 最大估分
        self.max_score: int = kw("max_score")

        # 当前可用估分
        self.current_score: int = kw("current_score")

    def _serialize(self):
        return {k: getattr(self, k, None) for k in self._to_serialize}

    async def preserve(self):
        """更新到redis"""
        await RedisDevicePayload.async_redis_db_instance.set(
            self.client_id, json.dumps(self._serialize())
        )
