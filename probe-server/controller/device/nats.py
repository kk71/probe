# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "NATSReqProbeDevicePost",
    "NATSReqProbeDeviceDelete",
    "NATSReqProbeDevicePut"
]

from utils.schema_utils import *
from mq.nats import NATSRequestHandler
from ..nats import *
from ..system_task import *


class NATSReqProbeDevicePost(NATSRequestHandler):
    """增加设备"""

    SUBJECT = "probe.device.post"

    @classmethod
    async def request(cls, device, **kwargs):
        ret = {
            "ip": device.ip_address if device.ip_address else "",
            "device_id": device.client_id,
            "device_type": device.device_type,
            "country": device.country,
            "province": device.province,
            "city": device.city,
            "carrier": device.carrier,
            "status": device.status,
            "schedule_time": {
                "start_time": device.start_time,
                "end_time": device.end_time
            },
            "task_limit": device.max_task_capacity,
            "remark": device.remark,
            "mac_address": device.mac_address,
            "client_version": device.client_version_to_str(),
            "down_time": device.disconnected_at
        }
        return ret


class NATSReqProbeDevicePut(NATSRequestHandler):
    """修改设备"""

    SUBJECT = "probe.device.put"

    @classmethod
    async def request(cls, device, **kwargs):
        ret = {
            "ip": device.ip_address,
            "device_id": device.client_id,
            "device_type": device.device_type,
            "country": device.country,
            "province": device.province,
            "city": device.city,
            "carrier": device.carrier,
            "status": device.status,
            "schedule_time": {
                "start_time": device.start_time,
                "end_time": device.end_time
            },
            "task_limit": device.max_task_capacity,
            "remark": device.remark,
            "mac_address": device.mac_address,
            "client_version": device.client_version_to_str(),
            "down_time": device.disconnected_at
        }
        return ret


class NATSReqProbeDeviceDelete(NATSRequestHandler):
    """删除设备"""

    SUBJECT = "probe.device.delete"

    @classmethod
    async def request(cls, device, **kwargs):
        ret = {
            "device_id": device.client_id
        }
        return ret


@ControllerNATSHandler.as_callback("probe.fe.device.delete")
async def nats_resp_probe_device_delete(msg):
    """node端操作删除设备"""
    msg = Schema({"device_id": scm_unempty_str}).validate(msg)
    client_id: str = msg["device_id"]
    from .all_device import AllDevice
    async with await AllDevice.get(client_id) as a_probe:
        await a_probe.delete()
    return {
        "status": True
    }


@ControllerNATSHandler.as_callback("probe.fe.device.put")
async def nats_resp_probe_device_put(msg):
    """node端操作修改设备"""
    from ..emqx import ControllerEMQXHandler
    msg = Schema({
        "device_id": scm_unempty_str,

        "country": scm_str,
        "country_name": scm_str,
        "province": scm_str,
        "province_name": scm_str,
        "city": scm_str,
        "city_name": scm_str,
        "carrier": scm_str,
        scm_optional("latitude"): scm_str,
        scm_optional("longitude"): scm_str,
        "remark": scm_str
    }, ignore_extra_keys=True).validate(msg)
    client_id = msg.pop("device_id")
    from .all_device import AllDevice
    async with await AllDevice.get(client_id) as a_probe:
        for k, v in msg.items():
            setattr(a_probe, k, v)
        to_update = {
            # 用于发送给拨测端要求拨测端修改的配置
            "PROBE_COMMENT": a_probe.remark
        }
        await ControllerEMQXHandler.publish_json(
            a_probe.client_id,
            SystemTaskReinitialize(to_update=to_update)._serialize_for_firing()
        )
    return {
        "status": True
    }

