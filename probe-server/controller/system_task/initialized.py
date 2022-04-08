# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemTaskInitialized"
]

from logger import *
from .base import *


class SystemTaskInitialized(SystemTask, metaclass=SCCLoggerMixin):
    """拨测端初始化结束"""

    TASK_TYPE = TaskType(SystemTask._SYSTEM_TASK_TYPE_1, "$initialized")

    def __init__(self, **kwargs):
        super(SystemTaskInitialized, self).__init__(**kwargs)
        self.probe_location = kwargs.pop("probe_location")

    def _serialize_for_firing(self, **kwargs) -> dict:
        return {
            **super()._serialize_for_firing(**kwargs),

            "probe_location": self.probe_location
        }
