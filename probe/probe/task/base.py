# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "Task",
    "TaskType"
]

import asyncio
import traceback
from typing import List

import prettytable

from core.task import *
from settings import Setting
from logger import SCCLoggerMixin
from utils.decorators import func_loop


class Task(BaseTask, metaclass=SCCLoggerMixin):
    """任务"""

    COLLECTED = []

    FAIL_CONTINUE = True

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "probe/task/")

    RELATIVE_IMPORT_TOP_PATH_PREFIX = str(Setting.SETTING_FILE_DIR)

    # 所有等待/正在执行的任务
    TASKS: List[asyncio.Task] = []

    # 一个清理周期内的完成率(仅代表任务结束，包括了正确结束和异常报错以及取消)
    TASKS_DONE_RATE: float = 0.0

    # 一个清理周期内的错误率(即t.exception()返回了结果的)
    TASKS_EXCEPTION_RATE: float = 0.0

    # 当前还在运行的任务占用的分数总和
    TASKS_SCORE_SUM: int = 0

    # 每次拨测任务占用的分数
    # TODO 各任务如需要自定义，重写这个值即可
    SCORE_PER_TASK: int = 3

    @classmethod
    def collect(cls):
        super().collect()
        pt = prettytable.PrettyTable(
            ["supported task_type", "description"],
            align="l",
            sortby="supported task_type"
        )
        for i in cls.COLLECTED:
            pt.add_row((str(i.TASK_TYPE), i.__doc__))
        print(pt)

    @classmethod
    async def generate_task(cls, **kwargs):
        """
        生成一个任务实例，并且开始运行它。
        :param kwargs:
        :return:
        """
        for pt in cls.COLLECTED:
            if pt.TASK_TYPE == TaskType(*kwargs["task_type"]):
                new_pt = pt(
                    task_type=kwargs.pop("task_type"),
                    **kwargs
                )
                t = asyncio.get_running_loop().create_task(
                    new_pt.run(), name=str(new_pt))
                # 把任务的对象扔给这个coroutine task
                t.task_object = new_pt
                cls.TASKS.append(t)
                return
        cls.logger.error(f"no suitable task type was found for {kwargs['task_type']=}!")

    @classmethod
    @func_loop
    async def task_cleaner(cls):
        """周期清楚已经完成或者超时/失败的任务"""
        while True:
            done_num = exception_num = 0
            supposed_to_clean = len(cls.TASKS)
            if supposed_to_clean:
                temp_sum_of_undone_tasks = 0
                for i in range(supposed_to_clean):
                    try:
                        t = cls.TASKS.pop()
                    except IndexError:
                        break
                    if t.done():
                        done_num += 1
                        exception_info = t.exception()
                        if exception_info is not None:
                            exception_num += 1
                            if Setting.DEBUG:
                                # for debugging
                                pt = prettytable.PrettyTable(["key", "value"], align="l")
                                pt.add_row(("task name", t.get_name()))
                                for s in t.get_stack():
                                    pt.add_row(("traceback", "\n".join(traceback.format_stack(s))))
                                pt.add_row(("exception info", str(exception_info)))
                                cls.logger.error(
                                    f"\ntask failed and was found "
                                    f"with the following exceptions:\n{pt}\n")
                        continue
                    pt = getattr(t, "task_object", None)
                    if pt:
                        temp_sum_of_undone_tasks += pt.SCORE_PER_TASK
                    cls.TASKS.insert(0, t)
                cls.TASKS_DONE_RATE = round(done_num / supposed_to_clean, 2)
                cls.TASKS_EXCEPTION_RATE = round(exception_num / supposed_to_clean, 2)
                cls.TASKS_SCORE_SUM = temp_sum_of_undone_tasks
            await asyncio.sleep(Setting.PROBE_TASK_CLEAN_INTERVAL)
