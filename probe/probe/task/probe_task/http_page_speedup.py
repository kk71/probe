# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
]

from typing import List, Union
from collections import defaultdict

import httpx
from furl import furl

from logger import *
from utils import sys_utils
from utils.dt_utils import *
from ..base import *
from .base import *
from .dns import *


@ProbeTask.need_collect()
class ProbeTaskHTTPPageSpeedUp(ProbeTaskDNSRelated, metaclass=SCCLoggerMixin):
    """HTTP拨测页面优化提速"""

    TASK_TYPE = TaskType("resource", "pageSpeedUp")

    # 缺省的单个url请求的超时秒
    DEFAULT_TIMEOUT = 2.0

    async def query_url(self,
                        url: str,
                        dns_server: str = None,
                        timeout: Union[float, int] = DEFAULT_TIMEOUT) -> dict:
        """
        用一个dns服务器去拨测单个URL
        :param url:
        :param dns_server:
        :param timeout:
        :return:
        """
        parsed_url = furl(url)
        domain = parsed_url.host
        ret = {
            "url": url,
            "domain": domain,
            "dns_server": dns_server,
            "results": (results := []),
            "probe_task_status": self.PROBE_STATUS_SUCCESSFUL,
            "create_time": arrow.now()
        }
        if sys_utils.if_legal_ipv4(domain):
            ips = [domain]
        else:
            try:
                ips = await self.resolve_domain(
                    domain=domain,
                    nameservers=[dns_server])
            except DomainDNSResolveFailedException as e:
                ret["probe_task_status"] = self.PROBE_STATUS_DOMAIN_RESOLVE_FAILED
                return ret
        for ip in ips:
            async with httpx.AsyncClient(
                    verify=False,
                    timeout=httpx.Timeout(timeout)) as c:
                parsed_url.host = ip
                reconstructed_url = parsed_url.tostr()
                result = {
                    "ip": ip,
                    "response_time": 0,
                    "probe_task_status": None
                }
                try:
                    resp = await c.get(reconstructed_url, headers={"host": domain})
                    result["response_time"]: float = resp.elapsed.total_seconds()
                    result["probe_task_status"] = self.PROBE_STATUS_SUCCESSFUL
                except httpx.TimeoutException:
                    result["probe_task_status"] = self.PROBE_STATUS_TIMEOUT
                except:
                    result["probe_task_status"] = self.PROBE_STATUS_FAILED
                results.append(result)
        return ret

    async def query_url_group(self,
                              urls: List[str],
                              dns_server: str,
                              all_get: bool = False,
                              timeout=DEFAULT_TIMEOUT) -> List[dict]:
        """
        拨测url列表
        :param urls:
        :param dns_server:
        :param all_get: 是否拨测列表中的每一个url。
                        不然以域名筛选，每个域名下如有多个url仅随机选取一个拨测
        :param timeout:
        :return:
        """
        if not all_get:
            domain_urls = defaultdict(list)
            for url in urls:
                domain_urls[furl(url).host].append(url)
            urls.clear()
            for domain, the_urls in domain_urls.items():
                urls.append(the_urls[0])
        ret = []
        for url in urls:
            r = await self.query_url(url, dns_server=dns_server, timeout=timeout)
            ret.append(r)
        return ret

    async def run(self, **kwargs):
        ret = []
        for a_dns in self.probe_data["dns_servers"]:
            for _ in self.target:
                ret.extend(await self.query_url_group(
                    self.probe_data["urls"], a_dns, self.probe_data["allGet"]))
        await self.commit(ret)
