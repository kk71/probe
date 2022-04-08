# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeTask",
    "TaskType",
    "Target",
    "ProbeData"
]

import time
import asyncio
from typing import Union, Optional, Dict

import sys_noti
import sys_noti.task
from settings import Setting
from utils.dt_utils import *
from utils.decorators import func_loop
from ..emqx import *
from ..nats import *
from ..probe_group import *
from ..device import *
from ..region import *
from task.base import *


class ProbeTask(Task):
    """拨测任务"""

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "scheduler/probe_task")

    NATS_HANDLER = SchedulerNATSHandler

    CACHED_DATA: Dict[str, "ProbeTask"] = dict()

    # mqtt对象
    EMQX_HANDLER = SchedulerEMQXHandler

    # 拨测分组对象
    PROBE_GROUP = SchedulerProbeGroup

    # 调试用：强制拨测周期，优先于DEBUG_INTERVAL_RATE
    DEBUG_INTERVAL: Optional[Union[float, int]] = None

    # 调试用：倍速拨测周期
    DEBUG_INTERVAL_RATE: Union[float, int] = 1

    async def whether_to_fire(self, time_now: arrow.Arrow) -> bool:
        """
        检查目前是否可以下发任务的逻辑
        :param time_now:
        :return:
        """
        if not self.interval:
            return False

        time_elapsed = (time_now - self.TASK_LAST_EXECUTION_TIME[self.task_id]).total_seconds()

        if self.interval <= time_elapsed:
            if not self.task_time:
                return True
            if self.task_time[0] and not self.task_time[1] \
                    and self.task_time[0] <= time_now:
                return True
            if not self.task_time[0] and self.task_time[1] \
                    and time_now <= self.task_time[1]:
                return True
            if all(self.task_time) and \
                    self.task_time[0] <= time_now <= self.task_time[1]:
                return True
        return False

    @classmethod
    @func_loop
    async def loop_fire(cls):
        while True:
            tasks_fired_num = 0
            for task_id, a_task in cls.CACHED_DATA.items():
                now = arrow.now()
                if await a_task.whether_to_fire(now):
                    cls.TASK_LAST_EXECUTION_TIME[a_task.task_id] = arrow.now()
                    asyncio.create_task(a_task.fire())
                    tasks_fired_num += 1

            if tasks_fired_num:
                cls.logger.info(f"{tasks_fired_num} task(s) fired")
            await asyncio.sleep(10)

    @classmethod
    def generate_task(cls, **kwargs) -> Optional["ProbeTask"]:
        the_task = super(ProbeTask, cls).generate_task(**kwargs)
        if the_task:
            if cls.DEBUG_INTERVAL is not None:
                cls.logger.warning(
                    f"currently interval was forced to "
                    f"set to {cls.DEBUG_INTERVAL}")
                the_task.interval = cls.DEBUG_INTERVAL
            if cls.DEBUG_INTERVAL_RATE != 1:
                cls.logger.warning(
                    f"currently interval was "
                    f"set to be multiplied by {cls.DEBUG_INTERVAL_RATE}")
                the_task.interval *= cls.DEBUG_INTERVAL_RATE
        return the_task

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kg = kwargs.get

        # 拨测任务下发区域
        self.regions = set()
        if self.group_id:
            # 即使指定了拨测分组，最后也是归属到区域
            self.regions = self.PROBE_GROUP.get(self.group_id)
        if kg("regions"):
            # 如果指定了拨测分组，仍然可以继续指定区域，取并集
            self.regions.update(kg("regions"))

    async def fire(self, **kwargs):
        """
        发送拨测任务
        后续拨测的发送对象是拨测端而不是组了。
        因此每个组里搜索到的拨测端都需要拨测一次。
        :param self:
        :param kwargs:
        :return:
        """
        fired_with_devices_num = 0
        for a_region, client_ids in Region.iter_region(self.regions):
            if not client_ids:
                self.notifier(sys_noti.NoProbeWithinRegion, target=a_region)
                continue
            for client_id in client_ids:
                await self.EMQX_HANDLER.publish_json(
                    topic=client_id,
                    payload=self._serialize_for_firing(
                        region_info=a_region
                    )
                )
                a_probe = InitializedDevice.get(client_id)
                self.logger.info(f"fired {self} to {a_probe}")

                # ====================================================
                # 检查冗余发送，用于调试
                if a_probe.fire_times > 1:
                    self.logger.info(
                        f"the fire_times of {a_probe} is {a_probe.fire_times}"
                        f", now going to fire another "
                        f"{a_probe.fire_times - 1} ...")
                    redundent_tasks = []
                    t1 = time.time()
                    temp_payload = self._serialize_for_firing(region_info=a_region)
                    for i in range(a_probe.fire_times - 1):
                        redundent_tasks.append(
                            asyncio.create_task(self.EMQX_HANDLER.publish_json(
                                topic=client_id,
                                payload=temp_payload
                            )
                        ))
                    t2 = time.time()
                    self.logger.info(f"asynchronously done with time: {t2 - t1}s")
                    await asyncio.wait(redundent_tasks)
                    t3 = time.time()
                    self.logger.info(f"done with time: {t3 - t1}s")

                # ====================================================

                fired_with_devices_num += 1
        if not fired_with_devices_num:
            await self.noti_no_probe_for_task(self.regions)

    async def noti_no_probe_for_task(self, regions, **kwargs):
        """
        发送无拨测可用设备告警
        :param regions:
        :param kwargs:
        :return:
        """
        self.notifier(
            sys_noti.task.NoProbeForTask,
            target=self,
            group_id=self.group_id,
            task_id=self.task_id,
            group_regions=regions,
            expire=self.interval
        )

    def _serialize_for_firing(self, **kwargs) -> dict:
        return {
            **super()._serialize_for_firing(**kwargs),

            "task_send_time": arrow.now(),
            "target": self.target,
            "probe_data": self.probe_data,
            "result_topic": self.result_topic,
            "gid": self.gid,
            "uid": self.uid
        }

    def serialize_for_api(self, **kwargs) -> dict:
        r = {
            "task_type": self.task_type
        }
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, set):
                v = list(v)
            r[k] = v
        return r
