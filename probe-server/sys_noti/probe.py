# Author: kk.Fang(fkfkbill@gmail.com)

from .base import *
from utils import const


class Probe(SysNotification):
    """拨测设备异常"""

    async def _to_nats(self):
        r = await super(Probe, self)._to_nats()
        if self.appendent.get("dev_name"):
            r["dev_name"] = self.appendent["dev_name"]
        if self.appendent.get("dev_ip"):
            r["dev_ip"] = self.appendent["dev_ip"]
        return r


class RegisterNotSync(Probe):
    """设备注册未同步到前端"""

    LEVEL = const.SYSTEM_NOTIFICATION_LEVEL_ERROR


class LowOnlineRate(Probe):
    """设备可用率低"""

    pass


class NoProbeWithinRegion(Probe):
    """当前区域内无可用拨测设备"""

    pass
