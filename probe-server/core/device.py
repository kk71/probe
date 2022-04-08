# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseProbeDevice"
]

from typing import Any, List

from .self_collecting_class import *
from .cached import *


class BaseProbeDevice(SelfCollectingFramework, BaseCached):
    """基础拨测端"""

    MAX_TASK_CAPACITY = 4

    @classmethod
    def generate_device(cls, *args, **kwargs) -> "BaseProbeDevice":
        raise NotImplementedError

    def __init__(self, **kwargs):
        self._keys_to_serialize = set()

        def k(x):
            self._keys_to_serialize.add(x)
            return kwargs[x]

        def kg(x, default_value=None, as_type=None):
            self._keys_to_serialize.add(x)
            ret = kwargs.get(x, default_value)
            if as_type and ret is not None:
                ret = as_type(ret)
            return ret

        # 拨测端唯一标识
        self.client_id: str = k("client_id")

        # 拨测端版本号
        self.client_version: List[str] = kg("client_version")

        # 拨测端MAC信息
        self.mac_address: str = kg("mac_address")

        # IP
        self.ip_address: str = kg("ip_address")

        # 负载上限，即同时可运行几个任务
        self.max_task_capacity: int = kg("max_task_capacity", self.MAX_TASK_CAPACITY)

        # 拨测端所在设备类型
        self.device_type: int = kg("device_type")

        # 首次连接时间，最后一次连上的时间，下线时间
        self.register_time: Any = kg("register_time")
        self.connected_at: Any = kg("connected_at")
        self.disconnected_at: Any = kg("disconnected_at")

        # 地理信息+运营商信息
        self.country: str = kg("country", as_type=str)
        self.country_name: str = kg("country_name", as_type=str)
        self.province: str = kg("province", as_type=str)
        self.province_name: str = kg("province_name", as_type=str)
        self.city: str = kg("city", as_type=str)
        self.city_name: str = kg("city_name", as_type=str)
        self.latitude: str = kg("latitude", as_type=str)
        self.longitude: str = kg("longitude", as_type=str)
        self.carrier: str = kg("carrier", as_type=str)

        # 区域运营商信息是否优先考虑跟随EMQ-X获得的IP去定位
        # 如果拨测端上报的IP是公网IP，则优先使用该IP查询到的地理运营商信息覆盖拨测端相应字段
        # 否则保留后台修改之后的信息
        self.region_follow_network = kg("region_follow_network", default_value=True)

        # 拨测端可用时间区间
        self.start_time: Any = kg("start_time")
        self.end_time: Any = kg("end_time")

        # 备注文本
        self.remark: str = kg("remark")

        # 拨测端在线状态
        self.status: str = kg("status")

        # 拨测端启用/禁用
        self.enabled: bool = kg("enabled", True)

        # 拨测端所在的容器完整id。如果不在容器内，这个值为None
        self.docker_container_id: str = kg("docker_container_id")

        # 支持的拨测任务类型(property)
        self._available_task_type: tuple = kg("available_task_type")

        # 拨测调度端确认一次任务下发后，同一个任务的下发次数(冗余下发)
        # 通常用于调试/压测
        self.fire_times: int = kg("fire_times", 1, int)

    @property
    def available_task_type(self):
        return self._available_task_type

    @available_task_type.setter
    def available_task_type(self, value):
        self._available_task_type = value

    def __str__(self):
        locations_and_carrier = [
            getattr(self, i, None)
            for i in ("province_name", "city_name", "carrier")
        ]
        locations_and_carrier = [i if i else "" for i in locations_and_carrier]
        return f"<ProbeDevice ({self.client_id}," \
               f" {'-'.join(locations_and_carrier)})>"

    def _serialize(self, keys_included=None):
        """
        :param keys_included: 只要这几个字段，为None则表示要全部
        :return:
        """
        kts = self._keys_to_serialize
        if keys_included and isinstance(keys_included, (list, tuple)):
            kts = keys_included
        r = {
            k: getattr(self, k, None) for k in kts
        }
        return r

    def get_location_info_dict(self) -> dict:
        """获取拨测端的地理位置信息字段"""
        return self._serialize(keys_included=(
            "country", "country_name",
            "city", "city_name",
            "province", "province_name",
            "longitude", "latitude",
            "carrier"
        ))

    def serialize(self):
        raise NotImplementedError

    @classmethod
    def get(cls, *args, **kwargs) -> "BaseProbeDevice":
        raise NotImplementedError

    def client_version_to_str(self):
        try:
            return ".".join([str(i) for i in self.client_version])
        except:
            return "0.0.1"
