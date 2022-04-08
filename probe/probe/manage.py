# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeManage"
]

import asyncio

from settings import Setting
from utils.dt_utils import *
from settings import Version

# 当前启用的拨测端管理对象
# TODO 该对象可能会随着reinit而变化，因此导入本模块不可用from .. import方法，
# TODO 必须用import ...方法导入本模块以使用CurrentProbeManage
CurrentProbeManage = None


class ProbeManage:
    """设备临时信息维护"""

    def __init__(self, min_client_version, probe_location, **kwargs):
        if Version < min_client_version:
            raise ValueError(
                f"current version {Version} is not suitable for reinitialization!!!")

        self.create_time = arrow.now()

        # 拨测端所在的地理运营商信息
        self.region = probe_location

        # 启动周期性的拨测任务状态上报
        asyncio.get_running_loop().create_task(self.payload_update())

    async def payload_update(self):
        from .system_feedback import SystemFeedbackProbePayload
        while self is CurrentProbeManage:
            await SystemFeedbackProbePayload().run()
            await asyncio.sleep(Setting.PROBE_PAYLOAD_UPLOAD_INTERVAL)

    def region_to_str(self):
        return f"{self.region.get('province_name')}-" \
               f"{self.region.get('city_name')}-" \
               f"{self.region.get('carrier')}"

    def __str__(self):
        return f"<ProbeManage " \
               f"created at {dt_to_str(self.create_time)} " \
               f"located in {self.region_to_str()}>"

    @classmethod
    async def set_manage(cls, probe_manage_instance: "ProbeManage"):
        global CurrentProbeManage
        CurrentProbeManage = probe_manage_instance
