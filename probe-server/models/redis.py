# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseRedis",
    "RedisDevice",
    "RedisDevicePayload",
    "RedisAuth",
    "RedisTaskProbingIdList",
    "RedisTaskStatisticsIdLatest",
    "RedisDNSOutNet"
]

from typing import List

import aioredis
from redis import Redis as redis_py

from core.self_collecting_class import *
from settings import Setting


class BaseRedis(SelfCollectingFramework):
    """基础redis"""

    COLLECTED: List["BaseRedis"] = []

    REDIS_DB: int = None

    redis_db_instance: redis_py = None

    async_redis_db_instance: aioredis.Redis = None

    @classmethod
    async def connect(cls):
        assert cls.REDIS_DB is not None
        cls.redis_db_instance = redis_py(
            host=Setting.REDIS_IP,
            port=Setting.REDIS_PORT,
            password=Setting.REDIS_PASSWORD,
            db=cls.REDIS_DB
        )
        cls.async_redis_db_instance = await aioredis.from_url(
            f"redis://{Setting.REDIS_IP}:{Setting.REDIS_PORT}",
            password=Setting.REDIS_PASSWORD,
            db=cls.REDIS_DB
        )

    @classmethod
    async def process(cls, collected: List["BaseRedis"] = None, **kwargs):
        if not collected:
            collected = cls.COLLECTED
        for m in collected:
            await m.connect()

    @classmethod
    def flush(cls):
        cls.redis_db_instance.flushdb()

    @classmethod
    def flush_all(cls):
        for m in cls.COLLECTED:
            m.flush()


class RedisTaskAlertConfig(BaseRedis):
    """
    拨测任务的告警配置备份
    原始配置是存在mysql里的，nodejs端同步一份冗余到redis里
    TODO 业务逻辑不涉及python端，全部在nodejs和java处理
    """
    REDIS_DB = 0


@BaseRedis.need_collect()
class RedisTaskProbingIdList(BaseRedis):
    """
    拨测任务的完成task_probing_id列表
    按照从新到旧的排列顺序
    """
    REDIS_DB = 2


@BaseRedis.need_collect()
class RedisTaskStatisticsIdLatest(BaseRedis):
    """
    统计的最后一次id
    """
    REDIS_DB = 3


@BaseRedis.need_collect()
class RedisDevice(BaseRedis):
    """设备信息"""
    REDIS_DB = 5


@BaseRedis.need_collect()
class RedisDevicePayload(BaseRedis):
    """设备负载状态"""
    REDIS_DB = 6


@BaseRedis.need_collect()
class RedisDNSOutNet(BaseRedis):
    """
    广东广电需求
    出网的IP信息，
    TODO 此库数据为java和python共享，如许修改结构，请协调java代码
    """
    REDIS_DB = 9


@BaseRedis.need_collect()
class RedisAuth(BaseRedis):
    """EMQ X ACL认证用"""
    REDIS_DB = 15

    @classmethod
    def flush(cls):
        super().flush()
        cls.init_for_internal_user()

    @classmethod
    def init_for_internal_user(cls):
        """初始化拨测系统所需要的账户和acl"""
        for username, rules in Setting.EMQ_REDIS_ACL.items():
            cls.redis_db_instance.hmset(f"mqtt_acl:{username}", rules)
        for username, rules in Setting.EMQ_REDIS_AUTH.items():
            cls.redis_db_instance.hmset(f"mqtt_user:{username}", rules)
