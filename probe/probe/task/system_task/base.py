# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemTask"
]

from typing import Dict

from logger import *
from ..base import *


class SystemTask(Task, metaclass=SCCLoggerMixin):
    """系统任务"""

    _SYSTEM_TASK_TYPE_1 = "SYSTEM_TASK"

    MIN_CLIENT_VERSION = [0, 0, 1]

    def __init__(self, **kwargs):
        kwargs["task_id"] = None
        super(SystemTask, self).__init__(**kwargs)

    async def _serialize_for_commit(self, **kwargs) -> Dict:
        return {}

    async def commit(self, **kwargs):
        """
        上报数据的方法
        一个任务的一次拨测，可以多次上报数据（数据两大或者数据时事性要求高的情况）
        :param kwargs:
        :return:
        """
        return
