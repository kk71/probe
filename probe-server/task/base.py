# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "TaskType",
    "Task",
    "Target",
    "ProbeData"
]

from typing import Dict, List, Optional, DefaultDict, Tuple
from collections import defaultdict

from utils.dt_utils import *
from settings import Setting
from utils.ensured_dict import *
from core.task import *
from cached import *
from mq.nats import NATSRequestHandler
from sys_noti.base import SCCSysNotificationLoggerMixin
from utils.schema_utils import *
from . import const


class NATSReqTaskGetAll(NATSRequestHandler):
    """获取全部任务"""

    SUBJECT = "probe.task.get"

    # TODO 缺省是3s，这里改成30s了，因为大数据对接的数据量太大
    # 后续考虑把任务做成差异更新
    TIMEOUT = 30

    @classmethod
    def verify_task_time(cls, x):
        if x is None:
            # 允许task_time为None即不需要限定拨测启动和停止时间
            return None
        if len(x) != 2:
            scm_raise_error("task_time has wrong length")
            return False
        return Schema([scm_or(None, scm_datetime)]).validate(x)

    @classmethod
    def response_schema(cls):
        return Schema([
            {
                "task_id": str,
                "type": scm_unempty_str,
                "service_type": scm_unempty_str,
                "cycle": scm_int,
                "task_time": scm_use(cls.verify_task_time),
                "probe_data": {
                    scm_optional(object): object
                },
                "target": [
                    {
                        "type": scm_unempty_str,
                        scm_optional(object): object
                    }
                ],
                "status": scm_one_of_choices(const.ALL_TASK_STATUS),
                "group_id": scm_int,
                scm_optional("uid", default=None): scm_int,
                scm_optional("gid", default=None): scm_int,
                scm_optional("pinned", default=False): scm_bool,
            }
        ], ignore_extra_keys=True)


class Target(EnsuredDict):
    """target"""

    type = EDV()
    data = EDV()


class ProbeData(EnsuredDict):
    """probe_data"""

    pass


class Task(BaseTask, Cached, metaclass=SCCSysNotificationLoggerMixin):
    """拨测任务"""

    RELATIVE_IMPORT_TOP_PATH_PREFIX = str(Setting.SETTING_FILE_DIR)

    # nats对象
    NATS_HANDLER = None

    TARGET: "Target" = Target

    PROBE_DATA: "ProbeData" = ProbeData

    # 当前系统中配置的全部拨测任务实例
    CACHED_DATA: Dict[str, "Task"] = dict()

    # 周期任务的上一次执行时间
    # task_id: arrow.Arrow
    TASK_LAST_EXECUTION_TIME: DefaultDict[str, arrow.Arrow] = defaultdict(
        lambda: arrow.now().shift(months=-1))  # 缺省时间为当前的前一月，这样默认就会立刻执行任务

    @classmethod
    async def create_task_dict(cls, original_list: List[Dict]):
        """创建任务的CACHED_DATA结构"""
        new_data = defaultdict()
        for a in original_list:
            if a["status"] == const.TASK_STATUS_ON:
                # 仅添加状态为启用的拨测任务
                new_task = cls.generate_task(**a)
                if new_task:
                    # 任务无法识别的情况下new_task为None
                    new_data[a["task_id"]] = new_task
        return new_data

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        ret = await cls.NATS_HANDLER.request(NATSReqTaskGetAll)
        # 处理从nats更新拿到的任务
        new_data = await cls.create_task_dict(ret)
        # 找出原有的pinned的任务
        for task_id, the_task in cls.CACHED_DATA.items():
            if the_task.pinned:
                # TODO 这里有个问题，如果nats取得的任务task_id和已有的pinned的任务task_id一致
                #      这里的nats取得的任务就会被取代
                new_data[task_id] = the_task
        cls.CACHED_DATA = new_data  # THIS IS THREAD-SAFE

    @classmethod
    def generate_task(cls, **kwargs) -> Optional["Task"]:
        validated_data = kwargs
        # task_type = (type, service_type)
        validated_data_task_type = TaskType(
            validated_data["type"],
            validated_data["service_type"]
        )
        for pt in cls.COLLECTED:
            if pt.TASK_TYPE == validated_data_task_type:
                return pt(
                    task_id=validated_data["task_id"],
                    task_type=validated_data_task_type,
                    interval=validated_data["cycle"],
                    task_time=validated_data["task_time"],
                    probe_data=validated_data["probe_data"],
                    target=validated_data["target"],
                    status=validated_data["status"],
                    group_id=validated_data["group_id"],
                    gid=validated_data["gid"],
                    uid=validated_data["uid"],
                    pinned=validated_data["pinned"]
                )
        cls.logger.debug(f"illegal task: {validated_data}")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kg = kwargs.get

        # 拨测任务执行周期(秒)
        self.interval: int = kg("interval")

        # 拨测的始末时间
        # None表示一直拨测
        self.task_time: Optional[Tuple] = kg("task_time")

        # 拨测主数据
        self.target: List[dict] = [self.TARGET(t) for t in kg("target")]

        # 拨测次数据
        self.probe_data: dict = self.PROBE_DATA(kg("probe_data"))

        # 组id
        self.gid: int = kg("gid")

        # 用户id
        self.uid: int = kg("uid")

        # 拨测结果上报频道
        self.result_topic: str = kg("result_topic", const.PROBE_DEFAULT_RESULT_TOPIC)

        # 固定任务。一般而言任务是持久存放在mysql里通过nats定时更新到scheduler的
        # 固定任务是通过restful api接口创建的任务，不会随着nats刷新而删除
        # 固定任务有一套自己的增删的restful api
        self.pinned: bool = kg("pinned", False)

        # 拨测分组可不指定
        self.group_id: Optional[int] = kg("group_id")
