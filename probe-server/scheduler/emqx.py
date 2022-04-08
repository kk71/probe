# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SchedulerEMQXHandler"
]

from mq.emqx import *


class SchedulerEMQXHandler(MQTTHandler):
    """监听emqx"""

    USER = "scheduler"
