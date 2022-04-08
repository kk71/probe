# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemFeedbackProbePayload"
]

from typing import Dict

from settings import Setting
from .base import *
from ..task import Task


class SystemFeedbackProbePayload(SystemFeedback):
    """拨测端负载汇报"""

    TOPIC = "probe/status"

    def __init__(self, **kwargs):
        super(SystemFeedbackProbePayload, self).__init__(**kwargs)
        self.client_id = Setting.get_client_id()
        self.current_capacity = len(Task.TASKS)
        self.max_capacity = Setting.PROBE_MAX_TASK_CAPACITY
        self.load_rate = round(self.current_capacity / self.max_capacity, 2)
        self.done_rate = Task.TASKS_DONE_RATE
        self.exception_rate = Task.TASKS_EXCEPTION_RATE
        # 分数计算
        self.max_score = 100  # 分数总和 TODO 后续需要根据性能去计算一个大概的值
        self.current_score = Task.TASKS_SCORE_SUM

        # output as local warning
        if self.current_capacity >= Setting.PROBE_MAX_TASK_CAPACITY:
            self.logger.warning(
                f"number of tasks reached the top {Setting.PROBE_MAX_TASK_CAPACITY=}! "
                f"consider change the value of it or, try to deliver less tasks.")

    async def _serialize_for_commit(self, **kwargs) -> Dict:
        return {
            **await super(SystemFeedbackProbePayload, self)._serialize_for_commit(**kwargs),

            "client_id": self.client_id,
            "current_capacity": self.current_capacity,
            "max_capacity": self.max_capacity,
            "load_rate": self.load_rate,
            "done_rate": self.done_rate,
            "exception_rate": self.exception_rate,
            "max_score": self.max_score,
            "current_score": self.current_score
        }

    @classmethod
    def calc(cls):
        """计算负载"""
        pass

    async def commit(self, **kwargs):
        kwargs["qos"] = 0  # 上报状态不需要太严格，允许一定量的丢失
        await super(SystemFeedbackProbePayload, self).commit(**kwargs)
