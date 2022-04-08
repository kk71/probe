# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemFeedbackInitialize"
]

from typing import Dict

from settings import Setting, Version
from .base import *
from utils.sys_utils import *
from ..task import *


class SystemFeedbackInitialize(SystemFeedback):
    """已注册的设备启动后初始化"""

    TOPIC = "probe/init"

    def __init__(self, **kwargs):
        super(SystemFeedbackInitialize, self).__init__(**kwargs)
        self.client_id = Setting.get_client_id()
        self.mac_address = get_mac_address()
        self.max_task_capacity = Setting.PROBE_MAX_TASK_CAPACITY
        self.version = Version
        self.device_type = get_device_type()
        self.remark = Setting.PROBE_COMMENT
        self.docker_container_id = get_docker_container_id()
        self.available_task_type = [i.TASK_TYPE for i in Task.COLLECTED]

    async def _serialize_for_commit(self, **kwargs) -> Dict:
        return {
            **await super(SystemFeedbackInitialize, self)._serialize_for_commit(**kwargs),

            "client_id": self.client_id,
            "mac_address": self.mac_address,
            "max_task_capacity": self.max_task_capacity,
            "version": self.version,
            "device_type": self.device_type,
            "remark": self.remark,
            "docker_container_id": self.docker_container_id,
            "available_task_type": self.available_task_type
        }
