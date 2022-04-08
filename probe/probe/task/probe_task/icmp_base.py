# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeTaskICMPBase"
]

from .dns import *


class ProbeTaskICMPBase(ProbeTaskDNSRelated):
    """ICMP协议相关的拨测"""

    # 单个地址拨测
    TARGET_TYPE_ADDRESS = "address"
    # 地址列表拨测
    TARGET_TYPE_ADDRESS_GROUP = "addressGroup"
