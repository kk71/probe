# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeGroup"
]

from typing import DefaultDict, Set, Tuple
from collections import defaultdict

from cached import *
from mq.nats import *
from utils.schema_utils import *


class NATSReqProbeGroup(NATSRequestHandler):
    """获取拨测组"""

    SUBJECT = "probe.group_detail.get"

    @classmethod
    def response_schema(cls):
        return Schema([
            {
                "group_id": scm_gt0_int,
                "country": scm_str,
                "province": scm_str,
                "city": scm_str,
                "carrier": scm_str
            }
        ], ignore_extra_keys=True)


class ProbeGroup(Cached):
    """拨测组，包含组的地理和运营商信息"""

    CACHED_DATA: DefaultDict[
        int,  # group_id
        Set[
            Tuple[str, str, str, str]  # country, province, city, carrier
        ]
    ] = None

    # 发送接受组信息的nats
    NATS_HANDLER = None

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        new_data = defaultdict(set)
        ret = await cls.NATS_HANDLER.request(NATSReqProbeGroup)
        for a_group_detail in ret:
            new_data[a_group_detail["group_id"]].add((
                str(a_group_detail["country"]),
                str(a_group_detail["province"]),
                str(a_group_detail["city"]),
                a_group_detail["carrier"]
            ))
        cls.CACHED_DATA = new_data  # THIS IS THREAD-SAFE

    @classmethod
    def get(cls, group_id: int) -> Set[Tuple[str, str, str, str]]:
        """查询某个拨测组"""
        return cls.CACHED_DATA.get(group_id, set())

    @classmethod
    def get_by_city(cls, city: str) -> dict:
        for group_id, d in cls.CACHED_DATA:
            if d["city"] == city:
                return d

    @classmethod
    async def content_on_update(cls, *args, **kwargs):
        await cls.content_initialize(nats_handler=cls.NATS_HANDLER)
