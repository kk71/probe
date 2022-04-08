# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeEMQXHandler"
]

from mq.emqx import *
from settings import Setting
from .task import Task
from .system_feedback import *


class ProbeEMQXHandler(MQTTHandler):
    """监听emqx"""

    USER = "probe"

    @classmethod
    async def on_connected(cls):
        await SystemFeedbackInitialize().run()


@ProbeEMQXHandler.as_callback("region/")
async def probe_client_id_message(message, data):
    """全局区域消息"""
    await Task.generate_task(**data)


@ProbeEMQXHandler.as_callback(Setting.get_client_id())
async def probe_client_id_message(message, data):
    """client_id消息"""
    await Task.generate_task(**data)
