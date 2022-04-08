# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemTask",
    "TaskType"
]

from settings import Setting
from core.task import *
from logger import *


class SystemTask(BaseTask, metaclass=SCCLoggerMixin):
    """系统任务"""

    _SYSTEM_TASK_TYPE_1 = "SYSTEM_TASK"

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "controller/system_task")

    RELATIVE_IMPORT_TOP_PATH_PREFIX = str(Setting.SETTING_FILE_DIR)

    def __init__(self, **kwargs):
        kwargs["task_id"] = None
        super(SystemTask, self).__init__(**kwargs)
