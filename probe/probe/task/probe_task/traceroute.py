# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = []

import re
import asyncio
import threading
from typing import List, Tuple

from icmplib import traceroute, Hop

from utils.dt_utils import *
from utils import sys_utils
from ..base import *
from logger import *
from .dns import *
from .icmp_base import *

if not sys_utils.if_root():
    raise OSError("traceroute needs to be run with root privilege!")


class ThreadingTraceroute(threading.Thread):
    """子线程异步traceroute"""

    def __init__(self, *args, **kwargs):
        super(ThreadingTraceroute, self).__init__(*args, **kwargs)
        self.result = None  # result saved here
        self.exception = None

    def run(self) -> None:
        try:
            self.result = traceroute(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e

    async def get_result(self) -> List[Hop]:
        while self.is_alive():
            await asyncio.sleep(1)
        if self.exception:
            raise self.exception
        return self.result


@Task.need_collect()
class ProbeTaskTraceroute(ProbeTaskICMPBase, metaclass=SCCLoggerMixin):
    """traceroute拨测"""

    TASK_TYPE = TaskType("network", "traceroute")

    # 需要过滤掉的route的ip的regex
    ROUTE_IP_REGEX_TO_EXCLUDE: Tuple[re.Pattern] = (
        re.compile(r"^172\.17\."),
    )

    def __init__(self, **kwargs):
        super(ProbeTaskTraceroute, self).__init__(**kwargs)
        # 设置用于域名拨测的dns服务器
        # 是个列表，但是实际拨测的时候只选取第一个域名服务器的第一个A记录解析结果IP
        self.traceroute_dns_servers = self.probe_data.get("dns_servers")
        if not self.traceroute_dns_servers:
            self.traceroute_dns_servers = self.get_default_nameservers()

        # 最大追溯跳数
        self.ttl: int = self.probe_data.get("ttl", 30)
        try:
            if isinstance(self.ttl, str):
                self.ttl = int(self.ttl)
        except ValueError:
            self.ttl = 30

        # 单跳的最大等待时间，单位s
        # 穿来的数据是ms，需要转成s
        self.timeout: float = self.probe_data.get("timeout", 3000.0)
        try:
            if isinstance(self.timeout, str):
                self.timeout = int(self.timeout)
        except ValueError:
            self.timeout = 3000.0
        self.timeout: float = self.timeout / 1000

    async def traceroute_address(self, destination: str) -> dict:
        """
        traceroute单个目标地址
        :param destination: 可以是IP或者域名，如果是域名会调用dns解析，获取A记录的第一条
        :return:
        """
        d = []
        ip = None
        try:
            if sys_utils.if_legal_ipv4(destination):
                ip = destination
            else:
                ip = await self.resolve_domain_first_ip(
                    domain=destination,
                    nameservers=self.traceroute_dns_servers)
            t = ThreadingTraceroute(kwargs={
                "address": ip,
                "max_hops": self.ttl,
                "count": 3,
                "timeout": self.timeout
            })
            t.start()
            d = await t.get_result()
            probe_task_status = self.PROBE_STATUS_SUCCESSFUL
            if not d:
                probe_task_status = self.PROBE_STATUS_FAILED
        except TimeoutError:
            probe_task_status = self.PROBE_STATUS_TIMEOUT
        except OSError as e:
            self.logger.error(e)
            probe_task_status = self.PROBE_STATUS_FAILED
        except DomainDNSResolveFailedException:
            probe_task_status = self.PROBE_STATUS_DOMAIN_RESOLVE_FAILED
            self.logger.error(
                f"domain resolving failed: {destination=}, "
                f"{self.traceroute_dns_servers=}")
        except Exception as e:
            self.logger.error(
                f"uncaught exception raised: {e}, {destination=}, {ip=}")
            probe_task_status = self.PROBE_STATUS_FAILED
        routes = [
            {
                "ip": i.address,
                "distance": i.distance,
                "packets_sent": i.packets_sent,
                "packets_received": i.packets_received,
                "packet_loss": i.packet_loss,  # since it's a rate, use 'packet' instead of 'packets'
                "min_rtt": i.min_rtt,
                "max_rtt": i.max_rtt,
                "avg_rtt": i.avg_rtt
            } for i in d if not any([
                len(re_t.findall(i.address)) != 0
                for re_t in self.ROUTE_IP_REGEX_TO_EXCLUDE])
        ]
        # 手动判断distance最大的值的ip是不是我的目标ip
        # 如果不是则认为此次拨测失败
        routes = sorted(routes, key=lambda x: x["distance"])
        if routes and routes[-1]["ip"] != ip:
            probe_task_status = self.PROBE_STATUS_FAILED
        return {
            # 任务里记录的traceroute目标(可能是ip或者域名)
            "destination": destination,
            # 实际traceroute的ip
            "ip": ip,
            "routes": routes,
            "create_time": arrow.now(),
            "probe_task_status": probe_task_status
        }

    async def traceroute_address_group(self,
                                       address_group: List[str]) -> List[dict]:
        """拨测traceroute列表"""
        ret = []
        for a in address_group:
            ret.append(await self.traceroute_address(a))
        return ret

    async def run(self, **kwargs):
        ret = []
        for target in self.target:
            if target["type"] == self.TARGET_TYPE_ADDRESS:
                ret.append(await self.traceroute_address(target["data"]))
            elif target["type"] == self.TARGET_TYPE_ADDRESS_GROUP:
                ret.extend(await self.traceroute_address_group(target["addresses"]))
            else:
                assert 0
        await self.commit(ret)
