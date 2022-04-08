# Author: kk.Fang(fkfkbill@gmail.com)

import json
import uuid
from copy import deepcopy
from typing import List, Dict, Any

from utils.ensured_dict import *
from utils import const
from utils.schema_utils import *
from .base import *
from .dns_related import *
from ..nats import *
from ..address_group import *
from ..device import *


class TargetPing(Target):

    TARGET_TYPE_ADDRESS_GROUP = "addressGroup"

    # 拨测的目标是domain的情况下，
    # domain是固定使用ips列表中的ip，还是每次拨测都重新解析域名获取ip
    # bool
    domainChecked = EDV(False)

    ips = EDV(list)

    # 拨测目标的类型：domain ip ...
    # str
    targetType = EDV()


class ProbeDataPing(ProbeDataDnsRelated):

    # float
    timeout = EDV(0.0)

    # int
    count = EDV(0)


@ProbeTask.need_collect()
class ProbeTaskPing(ProbeTaskDNSRelated):
    """ping拨测任务"""

    TASK_TYPE = TaskType("network", "ping")

    TARGET = TargetPing

    PROBE_DATA = ProbeDataPing

    def __init__(self, **kwargs):
        super(ProbeTaskPing, self).__init__(**kwargs)

    def _serialize_for_firing(self, region_info: dict, **kwargs) -> dict:
        r = super()._serialize_for_firing(region_info, **kwargs)
        r["target"] = deepcopy(r["target"])
        for a_target in r["target"]:
            if a_target["type"] == self.TARGET.TARGET_TYPE_ADDRESS_GROUP:
                address_group_id = a_target["data"]
                the_address_group = SchedulerCachedAddressGroup.get(address_group_id)
                a_target["addresses"] = list(the_address_group)
                a_target["address_group_name"] = the_address_group.name
        return r


class ProbeTaskPingOneShoot(ProbeTaskPing):
    """ping一次性拨测任务"""

    pass


@SchedulerNATSHandler.as_callback("probe.task.ping_result.one_shoot.verbose")
async def nats_resp_ping_result_one_shoot_verbose(data):
    """前端发起的一次性的ping"""
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
    the_sub_result_channel = \
        f"{const.EMQX_TEMP_TOPIC_PREFIX}one_shoot_verbose/{temp_task_id}"
    a_one_shoot_task = ProbeTaskPingOneShoot(
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
            ProbeTaskPingOneShoot.logger.debug(
                f"results coming from probe"
                f" for {a_one_shoot_task}: {results_root}")
            results = results_root.get("results", [])
            for r in results:
                the_probe = InitializedDevice.get(
                    results_root.get("device").get("client_id")
                )
                rst.append({
                    "device": the_probe._serialize(keys_included=(
                        "country", "province", "city", "carrier")),
                    **r
                })

    await SchedulerEMQXHandler.temp_subscription_with_cb(
        the_sub_result_channel, cb, ttl=timeout)
    return {
        "results": rst,
        "resp_timeout": timeout
    }
