# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemTaskReinitialize"
]

from typing import Dict, Optional

from .base import *


class SystemTaskReinitialize(SystemTask):
    """要求设备重新初始化"""

    TASK_TYPE = TaskType(SystemTask._SYSTEM_TASK_TYPE_1, "$reinit")

    def __init__(self, to_update: Optional[Dict] = None, **kwargs):
        super(SystemTaskReinitialize, self).__init__(**kwargs)
        self.to_update = to_update

    def _serialize_for_firing(self, **kwargs) -> dict:
        self.logger.info("sending reinitializing command ...")
        return {
            **super(SystemTaskReinitialize, self)._serialize_for_firing(**kwargs),

            # 用于告知拨测端，在重新初始化之前先更新这些信息
            "to_update": self.to_update
        }
