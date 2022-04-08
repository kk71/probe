# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseSystemNotification"
]

import json
import traceback

from core.self_collecting_class import *


class BaseSystemNotification(SelfCollectingFramework):
    """
    系统提示，通常用于向外界传达拨测系统本身的值得被关注的信息
    """

    # 提示的类型
    # TODO 不要手动指定
    TYPE: str = None

    # 提示的类型增量
    # TODO 需要手动指定
    SUB_TYPE: str = None

    # 描述这个消息
    DESCRIPTION: str = None

    # 通知等级
    LEVEL: int = None

    def _meta_method(cls):
        if cls.TYPE:
            cls.TYPE = f"{cls.TYPE}.{cls.SUB_TYPE}"
        else:
            cls.TYPE = cls.SUB_TYPE

    META_METHOD = _meta_method
    del _meta_method

    def __init__(self, detail=None, target=None, **kwargs):
        # 报错具体堆栈
        self.detail: str = detail if detail else traceback.format_exc()
        # 对象名称
        self.target = target
        # 抛出时间
        self.create_time = None
        # 附加信息
        self.appendent = kwargs

    def _to_json(self, **kwargs):
        """序列化提示数据"""
        try:
            # try to json.dumps
            json.dumps(self.target, ensure_ascii=False)
            target = self.target
        except:
            # if json.dumps fails, turn to use what the __str__ returns
            target = str(self.target)
        try:
            # try to json.dumps
            json.dumps(self.appendent, ensure_ascii=False)
            appendent = self.appendent
        except:
            # if json.dumps fails, turn to use what the __str__ returns
            appendent = str(self.appendent)
        return {
            "type": self.TYPE,
            "description": self.DESCRIPTION,
            "level": self.LEVEL,
            "target": target,
            "detail": self.detail.strip(),
            "create_time": self.create_time,
            "appendent": appendent
        }

    def to_json(self, **kwargs):
        raise NotImplementedError

    def to_logger(self, **kwargs):
        raise NotImplementedError

    def to_nats(self, **kwargs):
        raise NotImplementedError
