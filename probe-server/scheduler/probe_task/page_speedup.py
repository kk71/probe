# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ProbeTaskHTTPPageSpeedup"
]

from copy import deepcopy

from utils.ensured_dict import *
from .base import *
from .dns_related import *


class TargetHTTPPageSpeedUp(Target):

    TARGET_TYPE_URL = "url"


class ProbeDataHTTPPageSpeedUp(ProbeDataDnsRelated):

    # 该字段指出，同域名下如果出现多个url，是否对全部url都进行：
    # 1、访问，获取响应时间
    # 2、统计的时候统计同域名的全部url的均值，而不是固定使用某个url。
    # 以上第2条是以第1条为基准的，即：统计的时候只管从数据库捞取数据，
    # 如果捞到同域名多条拨测记录那么就进行均值操作。
    allGet = EDV()

    # 实际拨测的url列表
    urls = EDV(list)


@ProbeTask.need_collect()
class ProbeTaskHTTPPageSpeedup(ProbeTaskDNSRelated):
    """页面拨测优化任务"""

    TASK_TYPE = TaskType("resource", "pageSpeedUp")

    TARGET = TargetHTTPPageSpeedUp

    PROBE_DATA = ProbeDataHTTPPageSpeedUp

    def __init__(self, **kwargs):
        super(ProbeTaskHTTPPageSpeedup, self).__init__(**kwargs)

    async def fire(self, **kwargs):
        self.target = deepcopy(self.target)
        for a_target in self.target:
            if a_target["type"] == self.TARGET.TARGET_TYPE_URL:
                pass
            else:
                assert 0
        return await super(ProbeTaskHTTPPageSpeedup, self).fire(**kwargs)
