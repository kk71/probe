# Author: kk.Fang(fkfkbill@gmail.com)

from utils.schema_utils import *
from task.base import NATSReqTaskGetAll
from ..http_server import *
from .base import *


@SchedulerHTTPServer.as_view("debug_interval")
class ProbeTaskDebugIntervalHandler(BaseReq):
    """拨测任务调整倍速"""

    async def get(self):
        """请求所有任务当前缺省的倍速"""
        await self.resp({
            "debug_interval": ProbeTask.DEBUG_INTERVAL,
            "debug_interval_rate": ProbeTask.DEBUG_INTERVAL_RATE
        })

    async def post(self):
        """修改所有任务的缺省倍速"""
        param = await self.get_json_args(Schema({
            scm_optional("debug_interval"): scm_or(scm_and(scm_num, lambda x: x > 0), None),
            scm_optional("debug_interval_rate"): scm_and(scm_num, lambda x: x > 0)
        }))
        if "debug_interval" in param.keys():
            ProbeTask.DEBUG_INTERVAL = param["debug_interval"]
        if "debug_interval_rate" in param.keys():
            ProbeTask.DEBUG_INTERVAL_RATE = param["debug_interval_rate"]
        await self.resp_created()


@SchedulerHTTPServer.as_view()
class ProbeTaskPinnedTaskHandler(BaseReq):
    """任务增删查接口"""

    async def get(self):
        """请求所有任务列表"""
        param = await self.get_query_args(Schema({
            scm_optional("task_id"): scm_unempty_str,
            scm_optional("pinned"): scm_bool,
            scm_optional("task_type"): scm_dot_split_str
        }))
        if "task_type" in param.keys():
            param["task_type"] = TaskType(*param["task_type"])
        await self.resp({
            "tasks": [
                t.serialize_for_api()
                for t in ProbeTask.CACHED_DATA.values()
                if all([getattr(t, k) == v for k, v in param.items()])
            ]
        })

    async def post(self):
        """增加任务"""
        param = await self.get_json_args(NATSReqTaskGetAll.response_schema())
        r = await ProbeTask.create_task_dict(param)
        ProbeTask.CACHED_DATA.update(r)
        await self.resp_created()

    async def delete(self):
        """删除任务"""
        param = await self.get_query_args(Schema({
            "task_id": scm_unempty_str
        }))
        task_id = param["task_id"]
        if ProbeTask.CACHED_DATA.get(task_id):
            del ProbeTask.CACHED_DATA[task_id]
        await self.resp_created()
