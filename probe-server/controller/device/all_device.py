# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "AllDevice"
]

import json
import asyncio
from typing import List

from device import *
from sys_noti.base import *
from settings import Setting
from ..nats import *
from models.redis import RedisDevice
from utils.decorators import func_loop
from utils import const
from utils.dt_utils import *
from utils.emqx_utils import *
from ..system_task import *
from .nats import *
from ip_db import *


class AllDevice(Device, metaclass=SCCSysNotificationLoggerMixin):
    """所有状态的拨测端"""

    NATS_HANDLER = ControllerNATSHandler

    # 设备当前在线率
    ONLINE_RATE: float = 0

    # 缺省的设备地理信息
    DEFAULT_COUNTRY = "86"
    DEFAULT_COUNTRY_NAME = "中国"

    @classmethod
    async def get(cls, client_id: str) -> "AllDevice":
        """查询某个拨测端"""
        r = await RedisDevice.async_redis_db_instance.get(client_id)
        if r:
            return cls(**json.loads(r))
        else:
            return cls(
                client_id=client_id,
                register_time=arrow.now()
            )

    @classmethod
    async def all(cls) -> List["AllDevice"]:
        """全部拨测端"""
        ret = []
        async for client_id in RedisDevice.async_redis_db_instance.scan_iter():
            a_probe = await cls.get(client_id)
            if a_probe:
                ret.append(a_probe)
        return ret

    @classmethod
    @func_loop
    async def sync(cls):
        """同步更新拨测设备的状态信息，上下线时间等"""
        while True:
            client_info = {
                client["clientid"]: client
                for client in await EMQXHttpAPI.get_all_clients()
            }
            device_connection_status: List[bool] = []
            for a_probe in await cls.all():
                connection_info = client_info.get(a_probe.client_id)
                async with a_probe:
                    if connection_info:
                        if connection_info["connected"]:
                            a_probe.status = const.DEVICE_STATUS_ONLINE
                            a_probe.connected_at = connection_info["connected_at"]
                        else:
                            a_probe.status = const.DEVICE_STATUS_OFFLINE
                        a_probe.disconnected_at = connection_info.get(
                            "disconnected_at", a_probe.disconnected_at)
                    else:
                        # TODO 有些时候EMQX里的设备信息会被删掉（kick out）
                        a_probe.status = const.DEVICE_STATUS_OFFLINE
                        if not a_probe.disconnected_at:
                            a_probe.disconnected_at = dt_to_str(arrow.now())
                    device_connection_status.append(
                        a_probe.status == const.DEVICE_STATUS_ONLINE)
            cls.logger.info("probe device connection status is updated")
            # calc connection rate and pop sys notification if it's too low
            if device_connection_status:
                cls.ONLINE_RATE = round(
                    sum(device_connection_status) / float(len(device_connection_status)),
                    2
                )
            if cls.ONLINE_RATE < Setting.LOG_SYS_NOTI_PROBE_CONNECTION_RATE:
                # cls.notifier(sys_noti.LowOnlineRate, rate=cls.ONLINE_RATE)
                pass
            await asyncio.sleep(30)

    @classmethod
    @func_loop
    async def force_sync(cls):
        """强制更新全部设备信息至前端，因为有一定概率前端的数据会失去同步"""
        while True:
            for a_probe in await cls.all():
                if a_probe:
                    await cls.NATS_HANDLER.request_no_cb(
                        NATSReqProbeDevicePut, device=a_probe)
            await asyncio.sleep(60*60)

    def __init__(self, **kwargs):
        """
        TODO 拨测设备实例请务必用with语句执行操作，
        TODO with语句退出的时候会自动提交redis的更改，并且检查是否需要向nodejs同步更新
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.r_device = None
        self.old_serialized_data = None
        self.is_deleted: bool = False

    def init_transactions(self):
        self.r_device = RedisDevice.async_redis_db_instance.pipeline()
        self.old_serialized_data = self.serialize()

    async def __aenter__(self) -> "AllDevice":
        self.init_transactions()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.commit()

    async def commit(self, delete: bool = False, auto_sync: bool = True):
        """
        提交redis的transaction
        :param delete: 删除
        :param auto_sync: 如果发现probe信息改变了，是否触发nodejs同步
        :return:
        """
        if delete:
            self.r_device.delete(self.client_id)
            await self.NATS_HANDLER.request_no_cb(
                NATSReqProbeDeviceDelete, device=self)
            self.r_device = None
            self.is_deleted = True
        else:
            if self.is_deleted:
                self.logger.info(f"probe device {self} is marked deleted "
                                 f"so any operations after it's deleted "
                                 f"won't be proceeded.")
                return
            self.r_device.set(self.client_id, self.serialize())
            await self.r_device.execute()
            # if the probe info has changed, synchronize it to mysql
            new_serialized_data = self.serialize()
            if new_serialized_data != self.old_serialized_data:
                if auto_sync:
                    # to update device info to mysql
                    await self.NATS_HANDLER.request_no_cb(
                        NATSReqProbeDevicePut, device=self)
            self.init_transactions()

    def generate_topics_for_region(self) -> List[str]:
        return [
            "region/",  # 所有区域（即一个包含全部区域拨测点的topic）
            # f"region/{self.country}",
            # f"region/{self.province}",
            # f"region/{self.city}",
            # f"region/{self.carrier}",
            # f"region/{self.country}/{self.carrier}",
            # f"region/{self.province}/{self.carrier}",
            # f"region/{self.city}/{self.carrier}"
        ]

    def set_location_info_from_ipdb(self, ipdb_info):
        """从ipdb的数据结构设置拨测端的地理位置信息"""
        self.country = ipdb_info["idd_code"]
        self.country_name = ipdb_info["country_name"]
        self.province = ipdb_info["china_admin_code"][:2] + "0000"
        self.province_name = ipdb_info["region_name"]
        self.city = ipdb_info["china_admin_code"]
        self.city_name = ipdb_info["city_name"]
        self.carrier = ipdb_info["isp_domain"]
        self.latitude = ipdb_info["latitude"]
        self.longitude = ipdb_info["longitude"]

    async def initialize(self):
        """设备启动连接"""
        client_info = await EMQXHttpAPI.get_client_info(self.client_id)
        client_ip = client_info[0]["ip_address"]
        ipdb_info = IPDB.get(client_ip)
        if ipdb_info["idd_code"] \
                and ipdb_info["country_name"] != "局域网" \
                and self.region_follow_network:
            self.set_location_info_from_ipdb(ipdb_info)
        else:
            # 如果是局域网，或者指明了不要从IP更新地理运营商信息，
            # 则把国家改成默认的
            self.country = self.DEFAULT_COUNTRY
            self.country_name = self.DEFAULT_COUNTRY_NAME
        self.status = const.DEVICE_STATUS_ONLINE
        self.connected_at = dt_to_str(arrow.now())
        self.ip_address = client_ip
        self.capacity = self.max_task_capacity
        if not self.remark:
            self.remark = ""
        topics_to_subscribe = self.generate_topics_for_region()
        topics_to_subscribe.append(self.client_id)
        if not await EMQXHttpAPI.subscribe_to_topics(
                self.client_id, topics_to_subscribe):
            self.logger.error(
                f"{self} failed when subscribing to topics: {topics_to_subscribe}")
        self.logger.info(f"{self} initialized successfully")
        the_task = SystemTaskInitialized(
            probe_location=self.get_location_info_dict()
        )
        await EMQXHttpAPI.publish_topic(
            self.client_id,
            the_task._serialize_for_firing()
        )

        # initialize payload
        self.payload = DevicePayload(
            client_id=self.client_id,
            max_capacity=self.max_task_capacity
        )
        await self.payload.preserve()

    async def delete(self):
        """删除设备"""
        await self.commit(delete=True)
