# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseTask",
    "TaskType",
    "TASK_TYPE_PLACEHOLDER"
]

import json
from typing import List, Dict, Iterable

from .self_collecting_class import *


class TaskType(tuple):
    """规定任务类型"""

    def __new__(cls, *iterable: Iterable):
        try:
            assert len(iterable) == 2
            assert isinstance(iterable[0], str)
            assert isinstance(iterable[1], str)
            assert iterable[0] != "" and iterable[1] != ""
        except AssertionError as e:
            print(iterable)
            raise e
        return super(TaskType, cls).__new__(cls, iterable)

    def __str__(self, *iterable: Iterable):
        return f"{self[0]}-{self[1]}"

    def __copy__(self):
        return TaskType(*self)

    def __deepcopy__(self, memodict={}):
        return TaskType(*self)


# 空的任务类型，特殊需求
TASK_TYPE_PLACEHOLDER = TaskType("-", "-")


class BaseTask(SelfCollectingFramework):
    """
    基础任务base task：凡是任务，即拨测服务端向拨测端发送一次性的mqtt消息
    拨测任务probe task：用于一次拨测的任务
    系统任务system task：用于修改拨测端的状态，或者让拨测端作出某个和拨测没有直接关系的动作的请求。
    系统反馈system feedback: 特殊的一类任务，实际是由拨测端反馈给拨测服务端的信息。
    """

    # 任务类型
    TASK_TYPE: TaskType = None

    # 任务最低可用的拨测端版本号
    MIN_CLIENT_VERSION = [0, 0, 1]

    @classmethod
    async def generate_task(cls, *args, **kwargs) -> "BaseTask":
        """
        初始化一个任务对象，但是和__init__不同，这个初始化是多态的，
        即：可能以自己的子类去初始化
        初始化的子类是collect收集到的子类
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def __init__(self, **kwargs):
        kg = kwargs.get
        # 任务id
        self.task_id: str = kwargs["task_id"]
        # 任务类型
        self._task_type: TaskType = TaskType(*kg("task_type", self.TASK_TYPE))
        # 任务状态
        self.status: int = kg("status")
        # 最低版本号
        self.min_client_version: str = kg("min_client_version", self.MIN_CLIENT_VERSION)
        # 发送给（接受者的client_id列表）
        self.send_to: List[str] = kg("send_to", [])
        assert self.task_type == self.TASK_TYPE
        assert self.min_client_version == self.MIN_CLIENT_VERSION

    @property
    def task_type(self):
        return self._task_type

    @task_type.setter
    def task_type(self, value):
        if not value:
            value = []
        self._task_type = TaskType(*value)

    async def commit(self, **kwargs):
        """上报拨测数据"""
        raise NotImplementedError

    async def run(self, **kwargs):
        """执行拨测操作"""
        raise NotImplementedError

    async def _serialize_for_commit(self, **kwargs) -> Dict:
        """
        输出用于上报的数据(当前返回结构，便于重载)
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def serialize_for_feedback(self, **kwargs) -> str:
        """输出用于发送任务的数据"""
        return json.dumps(
            self._serialize_for_commit(**kwargs),
            ensure_ascii=False,
            indent=4)

    def to_str(self, **kwargs):
        """
        转为可读的文本
        :param kwargs: 请注意所有参数必须带默认值！
        :return:
        """
        return f"<{self.__class__.__name__} {self.task_id}({self.task_type})>"

    def __str__(self):
        return self.to_str()
