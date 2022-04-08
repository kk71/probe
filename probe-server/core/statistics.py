# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseStatistics"
]

import abc


class BaseStatistics(metaclass=abc.ABCMeta):
    """基础统计模块"""

    @abc.abstractmethod
    def run_statistics(self, *args, **kwargs):
        """
        开始统计分析
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def dispatch(self, *args, **kwargs):
        """
        获得统计结果后的结果发送/相应的操作。
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError
