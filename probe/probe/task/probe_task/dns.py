# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeTaskDNSRelated",
    "DomainDNSResolveFailedException"
]

from typing import List, Optional

import dns.resolver
import dns.rcode
import dns.rdatatype
import dns.rdataclass
from dns.asyncresolver import Resolver as DNSAsyncResolver, get_default_resolver

from logger import *
from utils.dt_utils import *
from ..base import *
from .base import *


class ProbeTaskDNS(ProbeTask, metaclass=SCCLoggerMixin):
    """DNS拨测"""

    # section的可选项
    ALL_SECTIONS = (
        SECTION_NAME_ANSWER := "answer",
        SECTION_NAME_AUTHORITY := "authority",
        SECTION_NAME_ADDITIONAL := "additional"
    )

    # 域名拨测
    TARGET_TYPE_DOMAIN = "domain"
    # 域名列表拨测
    TARGET_TYPE_DOMAIN_GROUP = "domain_group"

    DEFAULT_LIFETIME = 2.0

    @staticmethod
    def get_default_nameservers():
        """获取拨测端系统默认的dns服务器（最坏打算）"""
        return get_default_resolver().nameservers

    @staticmethod
    async def query_dns(domain: str,
                        nameservers: List[str],
                        rdtype: str = dns.rdatatype.A,
                        lifetime: float = DEFAULT_LIFETIME
                        ):
        """
        查询一次
        :param domain:
        :param nameservers:
        :param rdtype: 查询的类型
        :param lifetime: 整个查询的时长，超时则抛出异常并结束
        :return:
        """
        rsv = DNSAsyncResolver(configure=False)
        rsv.nameservers = nameservers
        rsv.lifetime = lifetime
        return await rsv.resolve(
            domain,
            rdtype=rdtype,
            raise_on_no_answer=False,
            tcp=False)

    @classmethod
    def _process_dns_resolve_result(cls, r):
        """
        处理dns记录的解析结果
        特殊情况，NS记录的result通常是带"."结尾的，而这个"."实际是可选的。
        为了便于前端校验，这里统一去掉结尾可能出现的"."
        :param r:
        :return:
        """
        ret = str(r)
        if ret.endswith("."):
            ret = ret[:-1]
        return ret

    @classmethod
    def pack_section(cls, qr, section_name: str) -> List[dict]:
        """
        包装section结构
        :param qr:
        :param section_name:
        :return:
        """
        ret = []
        if qr is None:
            return ret
        for i in getattr(qr.response, section_name):
            for a_result in i.items:
                ret.append({
                    "name": str(i.name),
                    "ttl": i.ttl,
                    "rdclass": dns.rdataclass.RdataClass(i.rdclass).name,
                    "rdtype": dns.rdatatype.RdataType(i.rdtype).name,
                    "result": cls._process_dns_resolve_result(a_result)
                })
        return ret

    def __init__(self, **kwargs):
        super(ProbeTaskDNS, self).__init__(**kwargs)

        # 拨测端所在机器默认的dns
        self.default_dns: List[str] = self.get_default_nameservers()

    async def query_domain(self,
                           rdtype: str,
                           domain: str,
                           dns_server: str,
                           timeout_retry: int = 3) -> List[dict]:
        """
        拨测单个域名
        :param rdtype: 查询的类型
        :param domain:
        :param dns_server:
        :param timeout_retry: 因为域名列表的dns解析频率很高，dns服务器可能会偶发地延迟非常大。
                              如果出现延迟很大而超时，则考虑重试次数
        :return:
        """
        ret = []
        for lifetime in [self.DEFAULT_LIFETIME * i
                         for i in range(1, timeout_retry + 1)]:
            ret = []
            r = None
            try:
                r = await self.query_dns(
                    domain,
                    rdtype=rdtype,
                    nameservers=[dns_server],
                    lifetime=lifetime
                )
                # response.time是秒，而es入库需要存毫秒
                delay = r.response.time * 1000
                ttl = getattr(r.rrset, "ttl", None)
                rcode = dns.rcode.Rcode(r.response.rcode()).name
                probe_task_status = self.PROBE_STATUS_SUCCESSFUL
            except dns.resolver.NXDOMAIN:
                delay = None
                ttl = None
                rcode = dns.rcode.NXDOMAIN.name
                probe_task_status = self.PROBE_STATUS_FAILED
            except dns.resolver.Timeout:
                # 本地查询的超时
                delay = None
                ttl = None
                rcode = None
                probe_task_status = self.PROBE_STATUS_TIMEOUT
            except Exception as e:
                exception_desc = str(e)
                if "answered REFUSED" in exception_desc:
                    delay = None
                    ttl = None
                    rcode = dns.rcode.REFUSED.name
                    probe_task_status = self.PROBE_STATUS_FAILED
                elif "answered SERVFAIL" in exception_desc:
                    delay = None
                    ttl = None
                    rcode = dns.rcode.SERVFAIL.name
                    probe_task_status = self.PROBE_STATUS_FAILED
                elif "timed out" in exception_desc:
                    # 服务器返回的超时
                    delay = None
                    ttl = None
                    rcode = None
                    probe_task_status = self.PROBE_STATUS_TIMEOUT
                else:
                    self.logger.error(
                        f"uncaught exception raised: {e}, "
                        f"{domain=}, {dns_server=}, {rdtype=}")
                    delay = None
                    ttl = None
                    rcode = None
                    probe_task_status = self.PROBE_STATUS_FAILED
            ret.append({
                "domain": domain,
                "rdtype": rdtype,
                "dns_server": dns_server,
                "delay": delay,
                "ttl": ttl,
                "rcode": rcode,
                "dns_response_status": rcode,  # TODO DEPRECATED
                "answer_section": self.pack_section(r, self.SECTION_NAME_ANSWER),
                "authority_section": self.pack_section(r, self.SECTION_NAME_AUTHORITY),
                "additional_section": self.pack_section(r, self.SECTION_NAME_ADDITIONAL),
                "create_time": arrow.now(),
                "probe_task_status": probe_task_status
            })
            if probe_task_status not in (
                    self.PROBE_STATUS_TIMEOUT,
                    self.PROBE_STATUS_FAILED):
                break  # 仅当超时的时候需要重新再拨测一次
        return ret

    async def query_domain_group(self,
                                 rdtype: str,
                                 domain_group: List[str],
                                 dns_server: str) -> List[dict]:
        """拨测域名列表"""
        ret = []
        for a_domain in domain_group:
            ret.extend(await self.query_domain(rdtype, a_domain, dns_server))
        return ret

    async def run(self, **kwargs):
        ret = []
        if not self.probe_data["dns_servers"]:
            # 拨测任务未配置dns的时候，使用拨测端所在机器默认的dns
            self.probe_data["dns_servers"] = self.default_dns
        for a_dns in self.probe_data["dns_servers"]:
            for target in self.target:
                # 区分查询什么字段，是A记录（即DNS记录）还是NS记录还是别的
                # typo: 老的数据结构写错了，应该叫rdtype
                target_rdtype: str = target["rrtype"]
                if target["type"] == self.TARGET_TYPE_DOMAIN:
                    ret.extend(await self.query_domain(
                        target_rdtype, target["data"], a_dns))
                elif target["type"] == self.TARGET_TYPE_DOMAIN_GROUP:
                    ret.extend(await self.query_domain_group(
                        target_rdtype, target["domains"], a_dns))
                else:
                    assert 0
        await self.commit(ret)


class DomainDNSResolveFailedException(Exception):
    """failed resolving domain to IP in ProbeTaskDNSRelated class(and it's sub-classes)"""

    pass


class ProbeTaskDNSRelated(ProbeTask):
    """
    拨测的步骤中涉及到dns的拨测
    这个类用于给拨测步骤中有dns解析的类去继承用，
    TODO 不要直接继承ProbeTaskDNS
    """

    # 拨测的拨测结果状态
    ALL_PROBE_STATUS = (
        PROBE_STATUS_SUCCESSFUL := "0",
        PROBE_STATUS_FAILED := "-1",
        PROBE_STATUS_TIMEOUT := "-2",
        PROBE_STATUS_DOMAIN_RESOLVE_FAILED := PROBE_STATUS_FAILED
    )

    @staticmethod
    async def resolve_domain(**kwargs) -> Optional[List[str]]:
        """
        使用dns拨测模块的dns解析去寻找域名的A记录
        如果找不到或者解析失败，则报错
        :param kwargs:
        :return:
        """
        try:
            return [i.address for i in (await ProbeTaskDNS.query_dns(**kwargs))]
        except Exception as e:
            raise DomainDNSResolveFailedException(str(e))

    @staticmethod
    async def resolve_domain_first_ip(**kwargs) -> Optional[str]:
        """
        使用dns拨测模块的dns解析去寻找域名的第一个A记录
        如果找不到或者解析失败，则报错
        :param kwargs:
        :return:
        """
        try:
            r = await ProbeTaskDNS.query_dns(**kwargs)
            return list(r)[0].address
        except Exception as e:
            raise DomainDNSResolveFailedException(str(e))

    @staticmethod
    def get_default_nameservers():
        """获取拨测端系统默认的dns服务器（最坏打算）"""
        return get_default_resolver().nameservers

    def __init__(self, **kwargs):
        super(ProbeTaskDNSRelated, self).__init__(**kwargs)

        # 拨测端所在机器默认的dns
        self.default_dns: List[str] = self.get_default_nameservers()
        if not self.probe_data.get("dns_servers"):
            # 拨测任务未配置dns的时候，使用拨测端所在机器默认的dns
            self.probe_data["dns_servers"] = self.default_dns


@ProbeTask.need_collect()
class ProbeTaskDNSMonitor(ProbeTaskDNS):
    """dns监控"""

    TASK_TYPE = TaskType("dns", "dnsMonitor")


@ProbeTask.need_collect()
class ProbeTaskDNSResolve(ProbeTaskDNS):
    """dns解析"""

    TASK_TYPE = TaskType("dns", "dnsResolve")


@ProbeTask.need_collect()
class ProbeTaskDNSHijack(ProbeTaskDNS):
    """dns防劫持"""

    TASK_TYPE = TaskType("dns", "dnsHijack")


@ProbeTask.need_collect()
class ProbeTaskDNSNSHijack(ProbeTaskDNS):
    """ns防劫持"""

    TASK_TYPE = TaskType("dns", "dnsNSHijack")

    async def query_domain(self,
                           rdtype: str,
                           domain: str,
                           dns_server: str,
                           timeout_retry: int = 3) -> List[dict]:
        ret = await super(ProbeTaskDNSNSHijack, self).query_domain(
            rdtype=rdtype,
            domain=domain,
            dns_server=dns_server,
            timeout_retry=timeout_retry
        )
        for item in ret:
            for section in item["answer_section"]:
                result: str = section["result"]
                section["results_a"] = []
                if result:
                    r: List[dict] = await super(ProbeTaskDNSNSHijack, self).query_domain(
                        rdtype="A",
                        domain=result,
                        dns_server=dns_server,
                        timeout_retry=timeout_retry
                    )
                    section["results_a"] = r
        return ret


@ProbeTask.need_collect()
class ProbeTaskDnsPrefer(ProbeTaskDNS):
    """给广东广电的需求增加的dns优选"""

    TASK_TYPE = TaskType("dns", "dnsPrefer")
