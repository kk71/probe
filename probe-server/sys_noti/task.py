# Author: kk.Fang(fkfkbill@gmail.com)

from utils import const

from .base import *


class Task(SysNotification):
    """任务异常"""

    def __init__(self, task_id, group_id, mail=None, message=None, **kwargs):
        self.task_id = task_id
        self.group_id = group_id
        self.message = message
        self.mail = mail
        super(Task, self).__init__(**kwargs)

    async def _to_nats(self):
        original_noti = self._to_json()
        r = await super(Task, self)._to_nats()
        r.update({
            "taskId": self.task_id,
            "groupId": self.group_id,
            "content": {
                "taskId": self.task_id,
                "message": self.message,
                "mail": self.mail,
                **original_noti
            }
        })
        return r


class NoDnsConfigured(Task):
    """任务无可用拨测dns"""

    pass


class NoProbeForTask(Task):
    """任务无可用拨测设备"""

    LEVEL = const.SYSTEM_NOTIFICATION_LEVEL_ERROR

    ENABLED = False
