# Author: kk.Fang(fkfkbill@gmail.com)

from ..http_server import *
from ..system_task import *
from .all_device import *


@ControllerHTTPServer.as_view("online_rate")
class DeviceOnlineRateHandler(BaseReq):

    async def get(self):
        """获取在线设备比例"""
        await self.resp({"online_rate": AllDevice.ONLINE_RATE})


@ControllerHTTPServer.as_view("force_reinitialize")
class DeviceForceReinitializeHandler(BaseReq):

    async def post(self):
        """立刻刷新全部设备信息"""
        from ..emqx import ControllerEMQXHandler
        await ControllerEMQXHandler.publish_json(
            "region/",
            SystemTaskReinitialize()._serialize_for_firing()
        )
        await self.resp({"msg": "all probe devices were forced to be reinitialized."})
