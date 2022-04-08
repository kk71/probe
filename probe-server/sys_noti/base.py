# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SysNotificationLoggerMixin",
    "SCCSysNotificationLoggerMixin",
    "SysNotification"
]

import json
import asyncio

import prettytable

from core.self_collecting_class import *
from settings import Setting
from mq.nats import NATSHandler
from core.system_notification import *
from logger import *
from utils.dt_utils import *
from utils.const import ALL_SYSTEM_NOTIFICATION_LEVEL, \
    SYSTEM_NOTIFICATION_LEVEL_ERROR, \
    SYSTEM_NOTIFICATION_LEVEL_WARNING


class SysNotificationMixin(type):

    def __init__(cls, name, bases, attrs):

        super().__init__(name, bases, attrs)

        # for system notification
        nats_handler = getattr(cls, "NATS_HANDLER", None)
        if not nats_handler:
            if issubclass(cls, NATSHandler):
                nats_handler = cls
        if not nats_handler:
            cls.logger.warning(f"missing nats client configured for {cls}, "
                               f"the system notification won't be popped through nats")

        def _notifier(*args, target=None, **kwargs):
            # 因为这个方法是一个奇葩的方法，理论上不接受cls或者self，
            # 但是目前发现self.的时候回把self传给第一个参数
            # 暂时不知道怎么解决，决定用*args循环一下取出想要的参数
            notification = None
            for a in args:
                try:
                    # issubclass针对实例会出错，这里就try一下吧
                    # 反正出错的肯定不是想要的
                    if issubclass(a, SysNotification):
                        notification = a
                        break
                except:
                    pass
            if not notification:
                raise TypeError("no notification type was given")
            loop = asyncio.get_running_loop()
            sys_noti = notification(
                target=target, **kwargs)
            # see if this notification should be warned or not
            if sys_noti.ENABLED:
                loop.create_task(sys_noti.to_nats(nats_handler))
                sys_noti.to_logger(cls.logger)

        # TODO use this to deliver sys-notification
        cls.notifier = _notifier
        del _notifier


class SysNotificationLoggerMixin(SysNotificationMixin, LoggerMixin):
    pass


class SCCSysNotificationLoggerMixin(
        SysNotificationLoggerMixin, SelfCollectingFrameworkMeta):
    pass


class SysNotification(BaseSystemNotification):

    # 用于收集全部的子类
    ALL_SUB_CLASSES = []

    DESCRIPTION = "拨测系统错误"

    LEVEL = SYSTEM_NOTIFICATION_LEVEL_WARNING

    # 根结点起名probe为了跟ems的alarm模块的命名同步
    TYPE = "probe"

    SUB_TYPE = ""

    # 是否启用。如果设置为False则忽略。
    ENABLED = True

    def _meta_method(cls):
        SUB_TYPE = getattr(cls, "SUB_TYPE", None)
        if SUB_TYPE is None:
            SUB_TYPE = cls.__name__
        cls.SUB_TYPE = None
        if cls.TYPE:
            cls.TYPE = f"{cls.TYPE}{SUB_TYPE}"
        else:
            cls.TYPE = SUB_TYPE
        # 如果指定了docstring，则优先将docstring作为描述文本
        if cls.__doc__:
            cls.DESCRIPTION = cls.__doc__

    META_METHOD = _meta_method
    del _meta_method

    def __init__(self, expire=60, dev_name="无设备", dev_ip="127.0.0.1", **kwargs):
        super().__init__(**kwargs)
        self.create_time = arrow.now()
        self.expire = expire
        self.dev_name = dev_name
        self.dev_ip = dev_ip
        assert self.LEVEL in ALL_SYSTEM_NOTIFICATION_LEVEL

    def to_json(self, **kwargs):
        json_serializable = dt_to_str(self._to_json(**kwargs))
        return json.dumps(json_serializable, ensure_ascii=False)

    def to_logger(self, logger, **kwargs):
        """在日志中展示notification"""
        pt = prettytable.PrettyTable(["keyword", "value"], align="l")
        for k, v in dt_to_str(self._to_json()).items():
            pt.add_row((k, v))
        s = f"System Notification output as log:\n{pt}"
        if self.LEVEL == SYSTEM_NOTIFICATION_LEVEL_WARNING:
            logger.warning(s)
        elif self.LEVEL == SYSTEM_NOTIFICATION_LEVEL_ERROR:
            logger.error(s)
        else:
            assert 0

    async def _to_nats(self):
        original_noti = self._to_json()
        # 冗余字段，前端展示用。
        original_noti["message"] = self.DESCRIPTION
        return {
            "addTime": original_noti["create_time"],
            "alarmType": 1,
            "code": self.TYPE,
            "content": original_noti,
            "devIp": self.dev_ip,
            "devName": self.dev_name,
            "expire": self.expire
        }

    async def to_nats(self, nats_handler: NATSHandler):
        """通过nats输出notification至ems的alarm模块"""
        await nats_handler.publish(
            Setting.LOG_SYS_NOTI_NATS_SUBJECT,
            await self._to_nats()
        )
