# Author: kk.Fang(fkfkbill@gmail.com)

import json
import uuid
from copy import deepcopy
from typing import List, Dict, Any

import sys_noti
from utils.ensured_dict import *
from utils.schema_utils import *
from utils import const
from .base import *
from .dns_related import *
from ..nats import *
from ..domain_group import *
from ..device import *


class TargetDns(Target):

    TARGET_TYPE_DOMAIN = "domain"
    TARGET_TYPE_DOMAIN_GROUP = "domain_group"

    # 所有rrtype的可选值
    ALL_RRTYPES = (
        RRTYPE_A := "A",
        RRTYPE_AAAA := "AAAA"
    )

    # A记录还是AAAA记录
    rrtype = EDV(RRTYPE_A)


class ProbeDataDns(ProbeData):

    dns_servers = EDV(list)


class ProbeTaskDNS(ProbeTaskDNSRelated):
    """DNS拨测任务"""

    TARGET = TargetDns

    PROBE_DATA = ProbeDataDns

    def _serialize_for_firing(self, region_info: dict, **kwargs) -> dict:
        r = super()._serialize_for_firing(region_info, **kwargs)
        r["target"] = deepcopy(r["target"])
        for a_target in r["target"]:
            if a_target["type"] == self.TARGET.TARGET_TYPE_DOMAIN_GROUP:
                domain_group_id = a_target["domain_group_id"]
                the_domain_group = SchedulerCachedDomainGroup.get(domain_group_id)
                a_target["domains"] = list(the_domain_group)
                a_target["domain_group_name"] = the_domain_group.name
        return r

    def _probe_domains(self):
        """
        返回拨测的类型（中文），以及拨测的域名（列表形式）
        :return:
        """
        for a_target in self.target:
            if "domain_group_name" in a_target.keys():
                type_name = "域名列表拨测"
                domain_group_id = a_target["domain_group_id"]
                the_domain_group = SchedulerCachedDomainGroup.get(domain_group_id)
                target = the_domain_group.name
            else:
                type_name = "域名解析拨测"
                target = a_target["data"]
            return type_name, target

    def to_str(self, for_nerd=False, **kwargs):
        type_name, target = self._probe_domains()
        if for_nerd:
            return f"拨测类型：{type_name} 拨测对象：{target}"
        return super(ProbeTaskDNS, self).to_str(**kwargs)

    def to_mail_info(self):
        type_name, target = self._probe_domains()
        return {
            "taskType": type_name,
            "target": target
        }

    async def noti_no_probe_for_task(self, regions, **kwargs):
        """
        发送无拨测可用设备告警
        :param regions:
        :param kwargs:
        :return:
        """
        self.notifier(
            sys_noti.task.NoProbeForTask,
            target=self,
            expire=self.interval + 60,  # 告警过期时间以任务周期+一点延时
            group_regions=regions,
            group_id=self.group_id,
            task_id=self.task_id,
            message=self.to_str(for_nerd=True),
            mail=self.to_mail_info()
        )


@ProbeTask.need_collect()
class ProbeTaskDNSMonitor(ProbeTaskDNS):

    TASK_TYPE = TaskType("dns", "dnsMonitor")


@ProbeTask.need_collect()
class ProbeTaskDNSResolve(ProbeTaskDNS):

    TASK_TYPE = TaskType("dns", "dnsResolve")


class ProbeTaskDNSResolveOneShoot(ProbeTaskDNSResolve):

    pass


@ProbeTask.need_collect()
class ProbeTaskDNSHijack(ProbeTaskDNS):

    TASK_TYPE = TaskType("dns", "dnsHijack")


@ProbeTask.need_collect()
class ProbeTaskDNSNSHijack(ProbeTaskDNS):

    TASK_TYPE = TaskType("dns", "dnsNSHijack")


@ProbeTask.need_collect()
class ProbeTaskDnsPrefer(ProbeTaskDNS):
    """
    dns速度优选任务
    基本功能：拨测特定的dns，通常是dns列表形式。使用客户提供的dns-IP映射（可能是接口或者通过数据文件）比对，
    给出相关的优化建议
    """

    TASK_TYPE = TaskType("dns", "dnsPrefer")


@SchedulerNATSHandler.as_callback("probe.task.dns_result.one_shoot")
async def nats_resp_dns_result_one_shoot(data):
    """前端请求发送一过性的dns拨测任务（获取dns解析结果）并等待返回"""
    from ..emqx import SchedulerEMQXHandler
    data = Schema({
        "probe_data": dict,
        "target": dict,
        scm_optional("group_id", default=None): scm_empty_as_optional(scm_gt0_int),
        scm_optional("regions", default=None): scm_empty_as_optional([scm_tuple]),
        scm_optional("resp_timeout", default=5): scm_int
    }).validate(data)
    assert any((data["group_id"], data["regions"]))
    timeout = data["resp_timeout"]  # 缺省的拨测端等待超时
    rst: List[str] = []
    temp_task_id = uuid.uuid4().hex
    the_sub_result_channel = f"{const.EMQX_TEMP_TOPIC_PREFIX}one_shoot/{temp_task_id}"
    a_one_shoot_task = ProbeTaskDNSResolveOneShoot(
        task_id=temp_task_id,
        probe_data=data["probe_data"],
        target=[data["target"]],
        group_id=data["group_id"],
        regions=data["regions"],
        result_topic=the_sub_result_channel
    )

    async def cb(msgs):
        await a_one_shoot_task.fire()
        async for msg in msgs:
            results_root = json.loads(msg.payload.decode("utf-8"))
            ProbeTaskDNSResolveOneShoot.logger.debug(
                f"results coming from probe"
                f" for {a_one_shoot_task}: {results_root}")
            results = results_root.get("results", [])
            for r in results:
                for answer_section in r["answer_section"]:
                    if answer_section.get("rdtype") in ("A", "AAAA", "NS"):
                        rst.append(answer_section["result"])

    await SchedulerEMQXHandler.temp_subscription_with_cb(
        the_sub_result_channel, cb, ttl=timeout)
    return {
        "results": list(set(rst)),
        "resp_timeout": timeout
    }


@SchedulerNATSHandler.as_callback("probe.task.dns_result.one_shoot.verbose")
async def nats_resp_dns_result_one_shoot_verbose(data):
    """前端请求发送一过性的dns拨测任务（获取dns解析结果）并等待返回:复杂信息版本"""
    from ..emqx import SchedulerEMQXHandler
    data = Schema({
        "probe_data": dict,
        "target": [dict],
        scm_optional("group_id", default=None): scm_empty_as_optional(scm_gt0_int),
        scm_optional("regions", default=None): scm_empty_as_optional([scm_tuple]),
        scm_optional("resp_timeout", default=5): scm_int
    }, ignore_extra_keys=True).validate(data)
    assert any((data["group_id"], data["regions"]))
    timeout = data["resp_timeout"]  # 缺省的拨测端等待超时
    rst: List[Dict[str, Any]] = []
    temp_task_id = uuid.uuid4().hex
    the_sub_result_channel =\
        f"{const.EMQX_TEMP_TOPIC_PREFIX}one_shoot_verbose/{temp_task_id}"
    a_one_shoot_task = ProbeTaskDNSResolveOneShoot(
        task_id=temp_task_id,
        probe_data=data["probe_data"],
        target=data["target"],
        group_id=data["group_id"],
        regions=data["regions"],
        result_topic=the_sub_result_channel
    )

    async def cb(msgs):
        await a_one_shoot_task.fire()
        async for msg in msgs:
            results_root = json.loads(msg.payload.decode("utf-8"))
            ProbeTaskDNSResolveOneShoot.logger.debug(
                f"results coming from probe"
                f" for {a_one_shoot_task}: {results_root}")
            results = results_root.get("results", [])
            for r in results:
                the_probe = InitializedDevice.get(
                    results_root.get("device").get("client_id")
                )
                rst.append({
                    "domain": r.get("domain"),
                    "delay": r.get("delay"),
                    "dns_response_status": r.get("rcode"),
                    "dns_server": r.get("dns_server"),
                    "device": the_probe._serialize(keys_included=(
                        "country", "province", "city", "carrier")),
                    "answer_section": r["answer_section"],
                    "authority_section": r["authority_section"],
                    "additional_section": r["additional_section"],
                })

    await SchedulerEMQXHandler.temp_subscription_with_cb(
        the_sub_result_channel, cb, ttl=timeout)
    return {
        "results": rst,
        "resp_timeout": timeout
    }
