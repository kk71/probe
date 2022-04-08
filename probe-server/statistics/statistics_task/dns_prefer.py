# Author: kk.Fang(fkfkbill@gmail.com)

import json
import asyncio
import traceback
from typing import Tuple, Optional
from collections import defaultdict

import requests

from utils.schema_utils import *
from settings import Setting
from .base import *
from ..models import *
from models.elasticsearch import *
from models.redis import RedisDNSOutNet
from ..nats import *


class DNSResolvedIP(BaseESInnerDoc):
    """解析到的IP以及附加信息"""

    ip = ESKeyword()

    # 是否出网
    outnet = ESBoolean()


class DNSResolvedIPGroup(BaseESInnerDoc):
    """dns对应解析到的ip的组"""

    dns = ESObject()

    ips = ESNested(DNSResolvedIP)

    # dns解析延时
    delay = ESFloat()

    # dns解析状态码
    dns_response_status = ESKeyword()

    # 拨测状态（文本的数字）
    probe_task_status = ESKeyword()

    def set_ip(self, ip: str, outnet: bool):
        """
        去重设置一条解析ip
        :param ip:
        :param outnet:
        :return:
        """
        for i in self.ips:
            if i.ip == ip:
                i.outnet = outnet
        r = DNSResolvedIP(ip=ip, outnet=outnet)
        self.ips.append(r)

    def calc_outnet_rate(self) -> float:
        """
        计算当前dns的解析结果集和的出网百分比
        :return:
        """
        if not len(self.ips):
            return 0.0
        outnet = [i for i in self.ips if i.outnet]
        return len(outnet) / float(len(self.ips))


class NATSReqTaskStatisticsDnsPreferResult(NATSRequestHandler):
    """每次保存新的统计数据之后，通过nats给nodejs发送一次最新的数据"""

    SUBJECT = "task.statistics.dns_prefer.result"

    @classmethod
    async def request(cls, stats_object: "BaseESStatisticsDoc", **kwargs):
        ret = stats_object.to_dict()
        return ret


class ESDocDNSPreferStatistics(BaseESStatisticsDoc):
    """
    dns出网解析的优选结果

    给定一系列dns，一个域名，拨测得到一系列ip
    针对给定的ip是否出网（根据给定的）
    """

    domain = ESKeyword()

    dns_ip_group = ESNested(DNSResolvedIPGroup)

    class Index:
        name = "dns-prefer-*"
        settings = {}

    def save(self,  **kwargs):
        # 删除原始已存在的全部统计数据
        r = self.search(). \
            query("term", task_id__keyword=self.task_id). \
            query("term", referenced_task_probing_id__keyword=self.referenced_task_probing_id)
        r.delete()
        # 写入
        super(ESDocDNSPreferStatistics, self).save(**kwargs)
        # 需要通过NATS给前端发送一下最新的结果
        t = StatisticsNATSHandler.request_no_cb(
            NATSReqTaskStatisticsDnsPreferResult, stats_object=self)
        asyncio.run(t)

    def get_dns_ip_group_by_dns(self,
                                dns: str,
                                add_if_not_existed: bool = True) -> Optional[DNSResolvedIPGroup]:
        """
        根据dns查询dns_ip_group
        :param dns:
        :param add_if_not_existed: 如果没搜到，是否直接增加一个新的记录
        :return:
        """
        for i in self.dns_ip_group:
            if i.dns == dns:
                return i
        if add_if_not_existed:
            r = DNSResolvedIPGroup(
                dns=dns
            )
            self.dns_ip_group.append(r)
            return r


@StatisticsTask.need_collect()
class StatisticsTaskDnsPrefer(StatisticsTask):
    """
    dns速度优选任务
    基本功能：拨测特定的dns，通常是dns列表形式。使用客户提供的dns-IP映射（可能是接口或者通过数据文件）比对，
    给出相关的优化建议
    """

    TASK_TYPE = TaskType("dns", "dnsPrefer")

    @classmethod
    def get_in_net_ip(
            cls,
            country: str,
            province: str,
            city: str,
            carrier: str,
            never_use_cache: bool = False) -> Tuple[str]:
        """
        按照地理运营商信息，查询网内的IP，用于判断是否出网
        :param country:
        :param province:
        :param city:
        :param carrier:
        :param never_use_cache: 不使用redis缓存
        :return:
        """
        # redis的key模板
        redis_key_template = f"{province}-{city}-{carrier}"
        cached_info = None
        if not never_use_cache:
            try:
                cached_info = RedisDNSOutNet.redis_db_instance.get(redis_key_template)
            except:
                pass
        if not cached_info:
            params = {"country": country, "province": province}
            if city:
                params["city"] = city
            if carrier:
                params["isp"] = carrier
            try:
                ret = requests.get(
                    f"http://{Setting.GDGD_OUTNET_API_IP}:{Setting.GDGD_OUTNET_API_PORT}"
                    f"/service/system/dimtable/ips/ipList/v1",
                    headers={"x-auth-token": Setting.GDGD_OUTNET_API_TOKEN},
                    params=params
                )
                cached_info = ret.json()
                cached_info = Schema([scm_unempty_str]).validate(cached_info)
            except:
                cls.logger.error(f"failed when fetching guangdong guangdian out-net data "
                                 f"from remote API with following info:"
                                 f"\n{traceback.format_exc()}")
                return tuple()
            if cached_info:
                redis_ex = Setting.GDGD_OUTNET_EXPIRING_TIME
            else:
                redis_ex = Setting.GDGD_OUTNET_EXPIRING_TIME_EMPTY
            RedisDNSOutNet.redis_db_instance.set(
                redis_key_template,
                json.dumps(cached_info),
                ex=redis_ex
            )
        return tuple(cached_info)

    @classmethod
    def set_all_records(cls, task_probing_id: str):
        """
        分析出单个task_probing_id的各个域名的解析结果
        只把数据组装起来，不考虑顺序
        :param task_probing_id:
        :return:
        """
        # domain: [DNSPreferObject, ...]
        docs = defaultdict(ESDocDNSPreferStatistics)
        original_docs = ESProbeData.search().query("term", task_probing_id=task_probing_id)
        for original_doc in original_docs.scan():

            # 拨测端的地理运营商信息，用于后续查询网内ip
            probe_location = {
                "country": original_doc.client_ip.country,
                "province": original_doc.client_ip.province,
                "city": original_doc.client_ip.city,
                "carrier": original_doc.client_ip.carrier
            }

            doc_of_the_domain = docs[original_doc.domain]
            doc_of_the_domain.domain = original_doc.domain
            doc_of_the_domain.task_id = original_doc.task_id
            doc_of_the_domain.task_type = original_doc.task_type
            doc_of_the_domain.referenced_task_probing_id = original_doc.task_probing_id
            doc_of_the_domain.client_id = original_doc.client_id
            doc_of_the_domain.client_ip = original_doc.client_ip
            doc_of_the_domain.probe_task_status = original_doc.probe_task_status
            # 当前original_doc拨测使用的dns
            dns: str = original_doc.dns_server_ip.ip
            # 当前dns的拨测的全部ip组
            dns_ips_group = doc_of_the_domain.get_dns_ip_group_by_dns(dns)
            dns_ips_group.dns = BaseESIPLocation.ipdb_to_location(dns)
            dns_ips_group.delay = original_doc.delay
            dns_ips_group.dns_response_status = original_doc.dns_response_status
            for an_answer in original_doc.answer:
                the_ip = an_answer.ip
                outnet = True
                in_net_ips = cls.get_in_net_ip(**probe_location)
                if the_ip in in_net_ips:
                    # 设置是否出网
                    outnet = False
                dns_ips_group.set_ip(the_ip, outnet)

            # TODO DEBUG
            # TODO 目前，es的dns_prefer数据已经不重要了，前端是不会去访问旧的分析结果的
            #      数据只给前端最新的，通过nats
            dns_ips_group.set_ip("1.1.1.1", True)

        return docs

    def _fire(self, **kwargs):
        for task_probing_id in self.get_task_probing_id():
            docs_of_the_task_probing_id = self.set_all_records(task_probing_id)
            for doc in docs_of_the_task_probing_id.values():
                doc.dns_ip_group.sort(key=lambda x: x.calc_outnet_rate())
                doc.save()
