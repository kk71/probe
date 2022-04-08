# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SystemTaskInitialized"
]

from utils.schema_utils import *
from ..base import *
from .base import *
from ...manage import *


@Task.need_collect()
class SystemTaskInitialized(SystemTask):
    """设备初始化结束，收到服务端发来的设备更新数据"""

    TASK_TYPE = TaskType(SystemTask._SYSTEM_TASK_TYPE_1, "$initialized")

    def __init__(self, **kwargs):
        super(SystemTaskInitialized, self).__init__(**kwargs)
        self.income_data = kwargs

    async def run(self, **kwargs):
        """
        拨测端反馈初始化请求，收到这个任务之后表明拨测端初始化结束
        这里修改的参数都是拨测端不会持久化的信息，譬如地理坐标运营商信息，每次启动都需要重新获取
        :param kwargs:
        :return:
        """
        d = Schema({
            'min_client_version': [int],
            'probe_location': {
                'country': scm_str,
                'country_name': scm_str,
                'city': scm_str,
                'city_name': scm_str,
                'province': scm_str,
                'province_name': scm_str,
                'longitude': scm_str,
                'latitude': scm_str,
                'carrier': scm_str
            }
        }, ignore_extra_keys=True).validate(self.income_data)
        new_manage = ProbeManage(**d)
        await ProbeManage.set_manage(new_manage)
        self.logger.info(f"probe initialized as {new_manage}.")
