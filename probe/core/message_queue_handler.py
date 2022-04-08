# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "MessageQueueHandler",
    "MessageQueueRequestHandler"
]

import json
from typing import Tuple, List, Dict, Callable

from core.self_collecting_class import *


class MessageQueueHandler(SelfCollectingFramework):
    """消息队列通用"""

    # 消息队列连接
    CONNECTOR = None

    # 收集到的callbacks
    CALLBACKS: List[Tuple[
        Tuple,    # *args
        Dict,     # **kwargs
        Callable  # the callback
    ]] = []

    @classmethod
    def gen_decorated_cb(cls, args, kwargs, a_callable):
        return a_callable

    @classmethod
    def as_callback(cls, *args, **kwargs):
        """
        需要收集的监听
        TODO 请小心使用该装饰器，如果你重写了cls.gen_decorated_cb，则该装饰器不能堆叠使用
        :param args:
        :param kwargs:
        :return:
        """
        def outer(a_callable):
            assert callable(a_callable)
            a_callable = cls.gen_decorated_cb(args, kwargs, a_callable)
            arguments = (args, kwargs, a_callable)
            if arguments not in cls.CALLBACKS:
                # 仅收集，不订阅，因为目前还不确定连接是否建立。
                cls.CALLBACKS.append(arguments)
            return a_callable
        return outer

    @classmethod
    def start(cls, *args, **kwargs):
        """
        开始监听
        注：该方法可用协程实现
        :return:
        """
        raise NotImplementedError

    @classmethod
    def publish(cls, **kwargs):
        """
        发送数据
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def request(cls, **kwargs):
        """
        发送请求/返回
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def serialize(cls, obj, **kwargs):
        """序列化"""
        return json.dumps(obj, ensure_ascii=False, indent=4)


class MessageQueueRequestHandler(SelfCollectingFramework):
    """消息队列的请求/返回"""

    # 不需要调用.collect即可获取全部的子类
    ALL_SUB_CLASSES = []

    # 超时时间（seconds）
    TIMEOUT = 5

    @classmethod
    async def request(cls, **kwargs):
        """发送请求"""
        raise NotImplementedError

    @classmethod
    async def response_cb(cls, **kwargs):
        """响应返回"""
        raise NotImplementedError

    @classmethod
    async def timeout(cls, **kwargs):
        """超时回调"""
        raise NotImplementedError
