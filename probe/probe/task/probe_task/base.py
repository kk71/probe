# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeTask"
]

import uuid
from typing import List, Dict

from settings import Setting, Version
from utils.dt_utils import *
from logger import SCCLoggerMixin
from ..base import *
from ... import manage


class ProbeTask(Task, metaclass=SCCLoggerMixin):
    """拨测任务"""

    # 结果切断为多个分多次传，None或者0表示不切断
    RESULTS_SLICED_TRANSFORM: int = None

    # 缺省的拨测结果状态
    ALL_PROBE_STATUS = (
        PROBE_STATUS_SUCCESSFUL := "0",
        PROBE_STATUS_FAILED := "-1",
        PROBE_STATUS_TIMEOUT := "-2"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 本次拨测的id
        self.task_probing_id: str = uuid.uuid4().hex
        kw = kwargs
        self.probe_data: dict = kw["probe_data"]
        self.target: List[dict] = kw["target"]
        self.task_send_time = arrow.get(kw["task_send_time"])  # 服务端任务发出时间
        self.task_receive_time = arrow.now()  # 拨测端收到任务的时间
        self.task_push_time = None  # 任务拨测结束推送拨测结果的时间
        self.result_topic: str = kw["result_topic"]
        self.gid = kw["gid"]
        self.uid = kw["uid"]

        # 调试选项，不通过emqx发出结果
        self._not_pop_result: bool = kw.get("_not_pop_result", False)

    async def _serialize_for_commit(self, results, **kwargs) -> Dict:
        """
        输出用于上报的数据(当前返回结构，便于重载)
        :param kwargs:
        :return:
        """
        self.task_push_time = arrow.now()
        return {
            "task_probing_id": self.task_probing_id,
            "task": {
                "task_id": self.task_id,
                "task_type": self.task_type,
                "task_send_time": self.task_send_time,
                "task_receive_time": self.task_receive_time,
                "task_push_time": self.task_push_time,
                "target": self.target,
                "probe_data": self.probe_data,
                "gid": self.gid,
                "uid": self.uid
            },
            "device": {
                "client_id": Setting.get_client_id(),
                "client_version": Version,
                "region": manage.CurrentProbeManage.region
            },
            "results": results
        }

    async def commit(self, results, **kwargs):
        """
        上报数据的方法
        一个任务的一次拨测，可以多次上报数据（数据两大或者数据时事性要求高的情况）
        :param results:
        :param kwargs:
        :return:
        """
        if self._not_pop_result:
            # 调试选项，不通过emqx发出结果
            return
        from ...emqx import ProbeEMQXHandler
        if not self.RESULTS_SLICED_TRANSFORM:
            await ProbeEMQXHandler.publish_json(
                topic=self.result_topic,
                payload=await self._serialize_for_commit(results, **kwargs)
            )
        else:
            while results:
                results_slice_to_transfer = []
                for i in range(self.RESULTS_SLICED_TRANSFORM):
                    try:
                        results_slice_to_transfer.append(results.pop())
                    except IndexError:
                        break
                if results_slice_to_transfer:
                    await ProbeEMQXHandler.publish_json(
                        topic=self.result_topic,
                        payload=await self._serialize_for_commit(
                            results_slice_to_transfer, **kwargs)
                    )

