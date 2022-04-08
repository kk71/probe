# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "LoggerMixin",
    "SCCLoggerMixin"
]

from core.self_collecting_class import *

from settings import Setting
from utils.log_utils import *


class LoggerMixin(type):

    def __init__(cls, name, bases, attrs):

        super().__init__(name, bases, attrs)

        # for logging
        cls.logger = get_bound_logger(name, level=Setting.LOG_LEVEL)


class SCCLoggerMixin(LoggerMixin, SelfCollectingFrameworkMeta):
    pass
