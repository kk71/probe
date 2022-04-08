# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ControllerEMQXHandler"
]

from typing import Dict, Union

from mq.emqx import *
from .device import *
from device import DevicePayload
from .system_task import *


class ControllerEMQXHandler(MQTTHandler):
    """监听emqx"""

    USER = "controller"

    @classmethod
    async def on_connected(cls):
        await cls.publish_json(
            "region/",
            SystemTaskReinitialize()._serialize_for_firing()
        )


@ControllerEMQXHandler.as_callback("probe/init")
async def probe_init(
        message,
        data: Dict[str, Union[str, int, list]]):
    """设备启动的时候与拨测服务端上报"""
    client_id = data["client_id"]
    async with await AllDevice.get(client_id) as d:
        d.mac_address = data["mac_address"]
        d.max_task_capacity = data["max_task_capacity"]
        d.client_version = data["version"]
        d.device_type = data["device_type"]
        d.remark = data["remark"]
        d.docker_container_id = data.get("docker_container_id")
        d.available_task_type = data.get("available_task_type")
        await d.initialize()


@ControllerEMQXHandler.as_callback("probe/status")
async def probe_status(
        message,
        data: Dict[str, Union[str, int, list]]):
    """设备上报负载情况"""
    p = DevicePayload(**data)
    await p.preserve()
