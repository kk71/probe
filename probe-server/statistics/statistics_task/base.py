# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "StatisticsTask",
    "TaskType",
    "Target",
    "ProbeDataStatistics",
    "run_on_thread"
]

import uuid
import json
import asyncio
from typing import List

from utils.decorators import func_loop, run_on_thread
from utils.ensured_dict import *
from utils.dt_utils import *
from task.base import *
from settings import Setting
from ..nats import StatisticsNATSHandler
from models.redis import RedisTaskProbingIdList


class ProbeDataStatistics(ProbeData):

    # 统计任务的周期，即拨测任务周期的倍数
    # 譬如：拨测任务的周期为60s，统计任务周期为1，即统计任务周期为60s*1=60s
    # 也就是拨测一次即统计一次
    interval = EDV(1)


class StatisticsTask(Task):
    """拨测任务的统计分析部分"""

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "statistics/statistics_task")

    NATS_HANDLER = StatisticsNATSHandler

    PROBE_DATA = ProbeDataStatistics

    # 目前正在运行的task_id
    RUNNING_TASK_ID = set()

    @classmethod
    @func_loop
    async def loop_fire(cls, *args, **kwargs):
        while True:
            tasks_fired_num = 0
            for task_id, a_task in cls.CACHED_DATA.items():
                now = arrow.now()
                if a_task.probe_data["interval"] > 0:
                    time_elapsed = (now - cls.TASK_LAST_EXECUTION_TIME[a_task.task_id]).total_seconds()
                    # if a_task.interval * a_task.probe_data["interval"] <= time_elapsed:
                    # TODO for debugging!!!
                    if 60 <= time_elapsed:
                        if task_id in cls.RUNNING_TASK_ID:
                            cls.logger.warning(
                                f"scheduled to fire {a_task}, "
                                f"but a previous process hasn't done yet.")
                            continue
                        cls.TASK_LAST_EXECUTION_TIME[a_task.task_id] = arrow.now()
                        # TODO 等到elasticsearch_dsl支持asyncio之后，需要切换成协程模式
                        a_task.fire()
                        tasks_fired_num += 1
                else:
                    pass
            if tasks_fired_num:
                cls.logger.info(f"{tasks_fired_num} task(s) fired")
            await asyncio.sleep(10)

    def __init__(self, **kwargs):
        super(StatisticsTask, self).__init__(**kwargs)

        # 统一的task_statistics_id
        self.task_statistics_id = uuid.uuid4().hex

    def get_task_probing_id(self) -> List[str]:
        """
        获取当前分析所需的最新的task_probing_id列表
        默认是获取拨测频率*分析频率时间区间内的task_probing_id列表
        :return:
        """
        task_probing_id_json_string = RedisTaskProbingIdList. \
            redis_db_instance.get(self.task_id)
        if not task_probing_id_json_string:
            task_probing_id_json_string = "[]"
        try:
            task_probing_ids = json.loads(task_probing_id_json_string)
        except json.JSONDecodeError:
            self.logger.error(f"no task_probing_id of {self} was found, "
                              f"it seems this task is just started to run and "
                              f"don't have any result yet?")
            return []
        statistics_interval = self.probe_data["interval"]
        return task_probing_ids[:statistics_interval]

    @run_on_thread
    def fire(self, **kwargs):
        try:
            self.RUNNING_TASK_ID.add(self.task_id)
            self.logger.info(f"firing {self} ...")
            self._fire(**kwargs)
        except Exception as e:
            self.RUNNING_TASK_ID.discard(self.task_id)
            raise e
        finally:
            self.RUNNING_TASK_ID.discard(self.task_id)

    def _fire(self, **kwargs):
        raise NotImplementedError
