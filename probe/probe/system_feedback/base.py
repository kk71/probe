# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemFeedback"
]

from typing import Dict

from utils.dt_utils import *
from core.task import *
from logger import *


class SystemFeedback(BaseTask, metaclass=SCCLoggerMixin):
    """拨测端主动发起的拨测服务端反馈"""

    # 当前系统反馈发送的频道
    TOPIC = None

    TASK_TYPE = TASK_TYPE_PLACEHOLDER
    
    def __init__(self, **kwargs):
        kwargs["task_id"] = None
        super(SystemFeedback, self).__init__(**kwargs)

    async def _serialize_for_commit(self, **kwargs) -> Dict:
        return {
            "create_time": arrow.now()
        }

    async def commit(self, **kwargs):
        """
        向拨测服务端上报数据的方法
        :param data:
        :param kwargs:
        :return:
        """
        from ..emqx import ProbeEMQXHandler
        return await ProbeEMQXHandler.publish_json(
            self.TOPIC,
            await self._serialize_for_commit(),
            **kwargs)

    async def run(self, **kwargs):
        await self.commit(**kwargs)
