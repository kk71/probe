# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = []

import traceback
from typing import Optional, List
from socket import gaierror

import arrow

from utils.dt_utils import *
from utils import sys_utils
from logger import *
from ..base import *
from .dns import *
from .icmp_base import *
from utils.ensured_dict import *


PING_PACKAGES = (
    PING_AIOPING := "aioping",
    PING_PING3 := "ping3"
)

# 当前使用何种ping的包
CURRENT_PING_PACKAGE = None


def try_which_package() -> str:
    for candidate in PING_PACKAGES:
        try:
            exec(f"import {candidate}")
            return candidate
        except ImportError:
            print(f"package {candidate} was not installed.")
    raise Exception(
        f"all candidates packages({PING_PACKAGES}) were not installed!")


# 根据系统是router，x86的linux，macos，以及是否为root，判断使用何种ping的包
if sys_utils.if_root() and sys_utils.if_macos():
    CURRENT_PING_PACKAGE = try_which_package()
elif not sys_utils.if_root() and sys_utils.if_macos():
    CURRENT_PING_PACKAGE = PING_PING3
elif sys_utils.if_root() and not sys_utils.if_macos():
    CURRENT_PING_PACKAGE = try_which_package()
elif not sys_utils.if_root() and not sys_utils.if_macos():
    raise OSError("ping needs to be run with root privilege on Linux!")
else:
    assert 0

# 导入对应的ping
if CURRENT_PING_PACKAGE == PING_PING3:
    from ping3 import ping
elif CURRENT_PING_PACKAGE == PING_AIOPING:
    from aioping import ping
else:
    assert 0


class PingReturn(EnsuredDict):
    """ping 单个返回"""

    # 任务里记录的ping目标(可能是ip或者域名)
    destination = EDV()

    # 实际ping的ip
    ip = EDV()

    delay = EDV()

    create_time = EDV(arrow.now())

    # ping拨测的ip的解析来源dns服务器
    dns_server: str = EDV()

    probe_task_status = EDV()


@Task.need_collect()
class ProbeTaskPing(ProbeTaskICMPBase, metaclass=SCCLoggerMixin):
    __doc__ = f"""Ping拨测({CURRENT_PING_PACKAGE})"""

    TASK_TYPE = TaskType("network", "ping")

    @staticmethod
    async def ping(
            ip: str,
            timeout: float,
            retry: int = 3) -> Optional[float]:
        """
        ping
        支持IP，如果传入域名，则使用拨测端所在系统的dns解析A记录随机一条aioping(或者第一条ping3)IP
        TODO 建议只传入IP
        :param ip:
        :param timeout:
        :param retry:
        :return:
        """
        ret = []
        exceptions = []
        for i in range(retry):
            try:
                # 注意，下面两个ping默认返回的值都是ping的延迟时间，单位s
                if CURRENT_PING_PACKAGE == PING_AIOPING:
                    r = await ping(ip, timeout)
                elif CURRENT_PING_PACKAGE == PING_PING3:
                    r = ping(ip, timeout=timeout)
                else:
                    assert 0
                if r:
                    r *= 1000  # es入库需要存毫秒
                ret.append(r)
            except Exception as e:
                exceptions.append(e)
        if len(exceptions) == retry:
            # 如果每次尝试ping都报错了，那么一定是没有结果的。raise第一次报错的信息
            raise exceptions[0]
        if not ret:
            # 理论上这个判断是不会进入的。
            return
        try:
            return sum(ret) / len(ret)
        except TypeError:
            return  # ret中可能包含None，因为IP未必可达

    def __init__(self, **kwargs):
        super(ProbeTaskPing, self).__init__(**kwargs)
        if CURRENT_PING_PACKAGE != PING_AIOPING:
            self.logger.warning(
                "using blocking ping implementation instead. "
                "consider changing to asyncio implementation!")
        self.ping_count = self.probe_data.get("count", 3)
        self.ping_timeout = self.probe_data.get("timeout", 3000) / 1000

    async def ping_address(self, destination: str, ip_candidate=()) -> List[dict]:
        """
        ping单个目标地址
        :param destination: 可以是IP或者域名，如果是域名会调用dns解析，获取A记录的第一条
        :param ip_candidate: 指定使用的拨测IP
        :return: list of dicts
        """
        ret = []
        d = None
        ips = None
        try:
            if sys_utils.if_legal_ipv4(destination):
                ips = [destination]
            else:
                if ip_candidate:
                    # destination是域名，并且指定了拨测的IP
                    ips = ip_candidate
                else:
                    # destination是域名，没指定拨测的IP
                    ips = await self.resolve_domain(
                        domain=destination,
                        nameservers=self.probe_data["dns_servers"])
        except DomainDNSResolveFailedException:
            probe_task_status = self.PROBE_STATUS_DOMAIN_RESOLVE_FAILED
            self.logger.error(
                f"domain resolving failed: {destination=}, "
                f"{self.probe_data['dns_servers']=}")
            ret.append(PingReturn(
                destination=destination,
                probe_task_status=probe_task_status
            ))

        for ip in ips:
            try:
                d = await self.ping(
                    ip,
                    timeout=self.ping_timeout,
                    retry=self.ping_count)
                probe_task_status = self.PROBE_STATUS_SUCCESSFUL
                if d is None:
                    # ping3 package: None return for timeout
                    probe_task_status = self.PROBE_STATUS_TIMEOUT
            except TimeoutError:
                # aioping package: TimeoutError for timeout
                probe_task_status = self.PROBE_STATUS_TIMEOUT
            except gaierror:
                probe_task_status = self.PROBE_STATUS_FAILED
            except OSError as e:
                self.logger.error(e)
                probe_task_status = self.PROBE_STATUS_FAILED
            except Exception as e:
                self.logger.error(
                    f"uncaught exception raised: {e}, {destination=}, {ip=}")
                self.logger.error(traceback.format_exc())
                probe_task_status = self.PROBE_STATUS_FAILED
            ret.append(PingReturn(
                destination=destination,
                ip=ip,
                delay=d,
                probe_task_status=probe_task_status,
                dns_server=self.probe_data["dns_servers"][0]
                if self.probe_data["dns_servers"] else None
            ))
        return ret

    async def ping_address_group(self,
                                 address_group: List[str]) -> List[dict]:
        """
        拨测ping列表
        :param address_group:
        :return:
        """
        ret = []
        for a in address_group:
            ret.extend(await self.ping_address(a))
        return ret

    async def run(self, **kwargs):
        ret = []
        for target in self.target:
            domain_checked: bool = target["domainChecked"]
            if target["type"] == self.TARGET_TYPE_ADDRESS and not domain_checked:
                # ip拨测
                ret.extend(await self.ping_address(target["data"]))

            elif target["type"] == self.TARGET_TYPE_ADDRESS and domain_checked:
                # 域名拨测-固定ip
                ret.extend(await self.ping_address(target["data"], target["ips"]))

            elif target["type"] == self.TARGET_TYPE_ADDRESS and not domain_checked:
                # 域名拨测-拨测时解析ip
                ret.extend(await self.ping_address(target["data"]))

            elif target["type"] == self.TARGET_TYPE_ADDRESS_GROUP:
                # 列表拨测（如果列表中包含域名，则拨测该域名的全部ip）
                ret.extend(await self.ping_address_group(target["addresses"]))

            else:
                assert 0
        await self.commit(ret)
