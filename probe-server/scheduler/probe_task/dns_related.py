# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeTaskDNSRelated",
    "ProbeDataDnsRelated"
]

from copy import deepcopy

import sys_noti
from utils.ensured_dict import *
from ..carrier_dns import *
from .base import *


class ProbeDataDnsRelated(ProbeData):

    dns_servers = EDV(list)


class ProbeTaskDNSRelated(ProbeTask):
    """
    拨测端的拨测步骤中，有需要进行dns解析步骤的任务
    需要dns解析，即需要指定dns服务器的字段。这里将该字段统一，序列化的时候使用统一的方式。
    """

    PROBE_DATA = ProbeDataDnsRelated

    def _serialize_for_firing(self, region_info: dict, **kwargs) -> dict:
        # 下面涉及修改拨测任务的结构，先深复制一份再做修改操作。
        r = super()._serialize_for_firing(**kwargs)
        if not r["probe_data"]["dns_servers"]:
            # 如果无自定义dns，则使用拨测端所在区域配置好的dns
            r["probe_data"] = deepcopy(r["probe_data"])
            r["probe_data"]["dns_servers"] = list(CarrierDNS.get(*region_info))

        # TODO 原本这里需要对找不到dns解析的任务进行告警
        #      鉴于需求方似乎不介意这个告警，暂时注释掉以提高并发（2021-7-2）
        # if not r["probe_data"]["dns_servers"]:
        #     self.notifier(
        #         sys_noti.NoDnsConfigured,
        #         target=self,
        #         task_id=self.task_id,
        #         group_id=self.group_id,
        #         expire=self.interval,
        #         mail={}
        #     )
        return r
