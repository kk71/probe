# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemTaskReinitialize"
]

from settings import Setting
from ..base import *
from .base import *


@Task.need_collect()
class SystemTaskReinitialize(SystemTask):
    """要求设备重新初始化"""

    TASK_TYPE = TaskType(SystemTask._SYSTEM_TASK_TYPE_1, "$reinit")

    def __init__(self, **kwargs):
        super(SystemTaskReinitialize, self).__init__(**kwargs)
        self.income_data = kwargs

    async def run(self, **kwargs):
        """
        拨测服务端请求重新初始化
        这里拨测服务端可以要求当前拨测端修改配置文件中的值
        注意：值的key是settings.py模块中的名称
        :param kwargs:
        :return:
        """
        self.logger.info("probe reinitializing acquired.")
        # 如果有要求修改拨测端的配置，会把配置的key放在这里。
        d = self.income_data.get("to_update", dict())
        if d:
            for k, v in d.items():
                setattr(Setting, k, v)
            Setting.save()
        from ...system_feedback import SystemFeedbackInitialize
        await SystemFeedbackInitialize().run()
