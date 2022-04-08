# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseSetting",
    "Setting",
    "Version"
]

import json
import uuid
from os import path
from pathlib import Path
from typing import List

import prettytable

from core.setting import *

# 当前使用的配置
Setting: "BaseSetting" = None


class BaseSetting(CoreSetting):
    """全局配置"""

    _tag = None

    # 用于收集子配置
    COLLECTED: "BaseSetting" = []

    @classmethod
    def set_current_setting(cls, tag: str):
        """
        启动的时候调用该方法选择以哪种配置启动，必须在任何项目相关的import之前调用。
        :param tag:
        :return:
        """
        global Setting
        for i in cls.COLLECTED:
            if i._tag == tag:
                Setting = i
                return Setting.print()

    @classmethod
    def print(cls):
        pt = prettytable.PrettyTable(["key", "value"], align="l", sortby="key")
        for k in cls.all_setting_keys():
            pt.add_row((k, cls.shorten(getattr(cls, k))))
        print(f"setting configuration of {cls}: \n{pt}")

    # =================================================================
    # 基础
    DEBUG = False
    TIMING_ENABLED: bool = CoreSetting.from_env("TIMING_ENABLED", 0, int)
    TIMING_THRESHOLD: int = 1
    SETTING_FILE_DIR: Path = Path(path.dirname(path.realpath(__file__)))
    STATIC_DIR: str = str(SETTING_FILE_DIR / "assets")
    HOST = SettingValueUnset
    # 缺省的缓存数据更新时间（秒）
    DEFAULT_CACHED_EXPIRY_TIME: int = 60

    # 内嵌http服务器相关
    HTTP_SERVER_ENABLED: bool = True
    HTTP_SERVER_IP = "0.0.0.0"
    HTTP_SERVER_PORT = 8888

    # 日志相关
    # 日志是否需要在已经输出到文件的情况下，再次输出到stdout
    LOG_NEED_STDOUT: bool = CoreSetting.from_env("LOG_NEED_STDOUT", False, int)
    # 日志文件的输出目录
    LOG_FILE_DIR: Path = SETTING_FILE_DIR / ".log"
    # 全体日志的输出级别: DEBUG INFO WARNING ERROR
    LOG_LEVEL: str = CoreSetting.from_env("LOG_LEVEL", "INFO", str)

    # 系统本身的告警相关
    LOG_SYS_NOTI_NATS_SUBJECT: str = "alarm.submit"  # 系统告警信息推送的nats主题
    LOG_SYS_NOTI_PROBE_CONNECTION_RATE: float = 0.9  # 设备可用率告警阈值

    # 统计模块相关
    # 统计的最后一条数据的id存留时间(即redis db 3)
    STATISTICS_LAST_RECORD_ID_EXPIRE: int = 60*60*24*7

    # EMQ/MQTT相关
    EMQ_DOMAIN = SettingValueUnset
    EMQ_HOST = SettingValueUnset
    EMQ_HTTP_PASSWORD = "public"
    EMQ_HTTP_PORT = 8081
    EMQ_HTTP_USERNAME = "admin"
    # eqmx回调的日志是否输出为DEBUG日志
    EMQ_CALLBACK_LOG = True
    EMQ_SERVICE_PORT = 1883
    EMQ_USE_SSL = False
    EMQ_USERS = {
        "scheduler": {
            "client_id": "scheduler",
            "username": "master",
            "password": "3a9994f6-1314-4d01-b400-6bea6dc6e010"
        },
        "controller": {
            "client_id": "controller",
            "username": "master",
            "password": "3a9994f6-1314-4d01-b400-6bea6dc6e010"
        },
        "viewer": {
            "client_id": lambda: f"viewer-{uuid.uuid4().hex}",
            "username": "master",
            "password": "3a9994f6-1314-4d01-b400-6bea6dc6e010"
        }
    }
    EMQ_REDIS_ACL = {
        "probe": {
            "%c": 3,
            "region/#": 1,
            "probe/#": 2,
            "results/#": 2,
            "temp_topic/#": 3
        },
        "master": {
            "#": 3
        },
        "results": {
            "results": 3
        }
    }
    EMQ_REDIS_AUTH = {
        "probe": {
            "password": "probe"
        },
        "master": {
            "password": "3a9994f6-1314-4d01-b400-6bea6dc6e010"
        },
        "results": {
            "password": "086eba14-cc93-11ea-9d06-88e9fe55b9e0"
        }
    }
    # emqx发出的json文本是否精简以缩小体积
    EMQ_PUBLISH_JSON_SIMPLIFY: bool = True

    # MySQL相关
    MYSQL_IP = SettingValueUnset
    MYSQL_PORT = 33066
    MYSQL_USERNAME = "ems"
    MYSQL_PASSWORD = "Ems4^Q7~e"
    MYSQL_DB_NAME = "confdb"
    MYSQL_ECHO = False  # orm是否打印sql日志

    # NAT相关
    NATS_IP = SettingValueUnset
    NATS_PORT = 4222
    NATS_USER = "ems"
    NATS_PASSWORD = "ems1234"
    NATS_CALLBACK_LOG = True

    # redis相关
    REDIS_IP = SettingValueUnset
    REDIS_PORT = 6379
    REDIS_PASSWORD = "ems1.0^123456"

    # elasticsearch相关
    ES_IP = SettingValueUnset
    ES_PORT = 9200
    ES_USERNAME = "elastic"
    ES_PASSWORD = "ems82!Jk&"

    # =================================================================
    # 广东广电出网的API接口的IP和端口
    GDGD_OUTNET_API_IP: str = "192.168.15.212"
    GDGD_OUTNET_API_PORT: int = 55303
    GDGD_OUTNET_API_TOKEN: str = "14f6f8e3-641e-4895-9ea1-991e63a417e1"
    # redis超时时间s
    GDGD_OUTNET_EXPIRING_TIME: int = 604800
    # redis超时时间s（针对空数据）
    GDGD_OUTNET_EXPIRING_TIME_EMPTY: int = 3600
    # =================================================================


# 版本号
with open(str(BaseSetting.SETTING_FILE_DIR / "VERSION"), "r") as z:
    Version: List[int] = json.loads(f"[{z.read().replace('.', ',')}]")


@BaseSetting.need_collect()
class JsonSetting(BaseSetting):
    """从JSON文件读取配置"""

    _tag = "json"

    _json_file = str(BaseSetting.SETTING_FILE_DIR / "setting.json")

    _pt = prettytable.PrettyTable([
        "overridden", "key", "value", "original value"], align="l", sortby="key")

    def _meta_method(cls):
        try:
            with open(cls._json_file, "r") as z:
                j = json.load(z)
        except FileNotFoundError:
            j = {}
        except json.JSONDecodeError as e:
            print(f"bad json file {cls._json_file}, use empty file instead: {e}")
            j = {}
        for k in cls.all_setting_keys():
            def_val = getattr(cls, k)
            if def_val is SettingValueUnset:
                def_val = None  # 把必须设置的值设置默认值为None
            derived_val = j.get(k, def_val)
            setattr(cls, k, derived_val)
            cls._pt.add_row((
                "    +    " if def_val != derived_val else " ",
                k,
                cls.shorten(derived_val),
                cls.shorten(def_val)
            ))

    META_METHOD = _meta_method
    del _meta_method

    @classmethod
    def print(cls):
        print(f"setting configuration of {cls}: \n{cls._pt}")


@BaseSetting.need_collect()
class DevSetting(BaseSetting):
    """测服配置"""

    _tag = "dev"

    DEBUG = True
    TIMING_ENABLED: bool = DEBUG
    HOST = "192.168.18.92"

    EMQ_DOMAIN = "dev.probe.yamucloud.com"
    EMQ_HOST = HOST

    NATS_IP = HOST

    MYSQL_IP = HOST

    REDIS_IP = HOST

    ES_IP = HOST


@BaseSetting.need_collect()
class ProdSetting(BaseSetting):
    """线上服配置"""

    _tag = "prod"

    DEBUG = True
    HOST = "192.168.18.93"

    EMQ_DOMAIN = "probe.yamucloud.com"
    EMQ_HOST = HOST

    NATS_IP = HOST

    MYSQL_IP = HOST

    REDIS_IP = HOST

    ES_IP = HOST
