# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "CarrierDNS"
]

from typing import Tuple, DefaultDict, Set, Optional
from collections import defaultdict

from utils.schema_utils import *
from mq.nats import NATSRequestHandler
from .nats import *
from cached import *


class NATSReqCarrierDNS(NATSRequestHandler):
    """获取运营商dns列表"""

    SUBJECT = "probe.local_dns.get"

    @classmethod
    def response_schema(cls):
        return Schema([
            {
                "country": scm_str,
                "province": scm_str,
                "carrier": scm_str,
                "city": scm_str,
                "ips": [scm_unempty_str]
            }
        ], ignore_extra_keys=True)


class CarrierDNS(Cached):
    """区域运营商的缺省拨测DNS"""

    NATS_HANDLER = SchedulerNATSHandler

    CACHED_DATA: DefaultDict[
        Tuple[Optional[str], Optional[str], Optional[str], Optional[str]],  # (地区信息字段)
        Set[str]  # set{dns的ip}
    ] = None

    # 为None的表示强制设置为None，为True的表示保留原值
    MASKS = (
        (True, True, True, True),
        (True, True, True, None),
        (True, True, None, None),
        (True, None, None, None),
        (True, True, None, True)
    )

    @staticmethod
    def alter_by_mask(array, mask):
        r = []
        for i in range(len(mask)):
            if mask[i]:
                r.append(array[i])
            else:
                r.append(None)
        return tuple(r)

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        new_data = defaultdict(set)
        r = await cls.NATS_HANDLER.request(NATSReqCarrierDNS)
        for i in r:
            ks = [i["country"], i["province"], i["city"], i["carrier"]]
            # 把任何有字文本以外的都当作空
            ks = tuple([i if i else None for i in ks])
            new_data[ks] = set(i["ips"])
        cls.CACHED_DATA = new_data  # THIS IS THREAD-SAFE

    @classmethod
    def get(cls,
            country: str,
            province: str,
            city: str,
            carrier: str) -> Tuple[str]:
        """查询dns服务器"""
        ks = [country, province, city, carrier]
        for m in cls.MASKS:
            ks_to_range = cls.alter_by_mask(ks, m)
            r = cls.CACHED_DATA.get(ks_to_range, tuple())
            if r:
                return r
        return tuple()
