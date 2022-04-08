# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseSetting",
    "Setting",
    "Version"
]

import json
import uuid
import traceback
from os import path
from pathlib import Path
from typing import List

import prettytable

from core.setting import *

# 当前使用的配置
Setting: "JsonSetting" = None


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
    SETTING_FILE_DIR: Path = Path(path.dirname(path.realpath(__file__)))
    # 调试模式
    DEBUG: bool = False
    # 日志是否输出到stdout
    LOG_NEED_STDOUT: bool = False
    # 日志输出等级
    LOG_LEVEL: str = "INFO"
    TIMING_ENABLED: bool = True
    TIMING_THRESHOLD: int = 0
    PROBE_COMMENT = ""

    # 性能上报相关
    # 最大业务承载量（只展示不强制要求）
    PROBE_MAX_TASK_CAPACITY: int = 50
    # 检查已完成任务的周期
    PROBE_TASK_CLEAN_INTERVAL: int = 10
    # 周期性的拨测端负载上报频率
    PROBE_PAYLOAD_UPLOAD_INTERVAL: int = 30

    # 拨测服务端EMQX配置
    EMQ_CALLBACK_LOG = True
    EMQ_DOMAIN = SettingValueUnset
    EMQ_SERVICE_PORT = 1883
    EMQ_USE_SSL: bool = True
    EMQ_USERS = {
        "probe": {
            "username": "probe",
            "password": "probe",
            "client_id": lambda: uuid.uuid4().hex
        }
    }
    # emqx发出的json文本是否精简以缩小体积
    EMQ_PUBLISH_JSON_SIMPLIFY: bool = True


# 版本号
with open(str(BaseSetting.SETTING_FILE_DIR / "VERSION"), "r") as z:
    Version: List[int] = json.loads(f"[{z.read().replace('.', ',')}]")


@BaseSetting.need_collect()
class JsonSetting(BaseSetting):
    """从JSON文件读取配置"""

    _tag = "json"

    # 配置文件json
    _json_file = str(BaseSetting.SETTING_FILE_DIR / "config.json")

    # 缺省配置文件json
    _json_file_default = str(BaseSetting.SETTING_FILE_DIR / "config.default.json")

    def _meta_method(cls):
        return cls.load()

    META_METHOD = _meta_method
    del _meta_method

    @classmethod
    def print(cls):
        print(f"setting configuration of {cls}: \n{cls._pt}")

    @classmethod
    def load(cls):
        cls._pt = prettytable.PrettyTable([
            "overridden", "key", "value", "original value"], align="l", sortby="key")
        # TODO 临时的变量，用于从旧的配置里读取client_id
        old_client_id = None
        try:
            with open(cls._json_file, "r") as z:
                j = json.load(z)
            old_client_id = j.get("device_id")
        except FileNotFoundError:
            j = {}
        except json.JSONDecodeError as e:
            print(f"bad json file {cls._json_file}, use empty file instead: {e}")
            j = {}
        try:
            with open(cls._json_file_default, "r") as z:
                jd = json.load(z)
        except FileNotFoundError:
            jd = {}
        except json.JSONDecodeError as e:
            print(f"bad json file {cls._json_file_default}, use empty file instead: {e}")
            jd = {}
        for k in cls.all_setting_keys():
            def_val = jd.get(k, getattr(cls, k))
            derived_val = j.get(k, def_val)
            if derived_val is SettingValueUnset:
                derived_val = None
            setattr(cls, k, derived_val)
            cls._pt.add_row((
                "    +    " if def_val != derived_val else " ",
                k,
                cls.shorten(derived_val),
                cls.shorten(def_val)
            ))

    @classmethod
    def save(cls, clear: bool = False):
        """
        保存当前配置
        :param clear: 不保存当前数据，而是清空配置
        :return:
        """
        try:
            with open(cls._json_file, "w") as z:
                if not clear:
                    d = {
                        k: getattr(cls, k) for k in cls.all_setting_keys()
                    }
                else:
                    d = {}
                json.dump(d, z, ensure_ascii=False, indent=4)
        except:
            print(traceback.format_exc())
            print("* failed while writing to config file.")

    @classmethod
    def get_client_id(cls):
        """安全获取client_id"""
        r = cls.EMQ_USERS["probe"]["client_id"]
        if isinstance(r, str):
            return r
        if callable(r):
            new_client_id = cls.EMQ_USERS["probe"]["client_id"] = r()
            print(f"generated brand new client_id {new_client_id}")
            cls.save()
            return new_client_id


@BaseSetting.need_collect()
class DevSetting(JsonSetting):
    """测服配置"""

    _tag = "dev"

    EMQ_DOMAIN = "dev.probe.yamucloud.com"
    EMQ_SERVICE_PORT = 8883


@BaseSetting.need_collect()
class ProdSetting(JsonSetting):
    """线上服配置"""

    _tag = "prod"

    EMQ_DOMAIN = "probe.yamucloud.com"
    EMQ_SERVICE_PORT = 8883


@BaseSetting.need_collect()
class StandAloneSetting(JsonSetting):
    """独立搭建服配置"""

    _tag = "standalone"

    EMQ_SERVICE_PORT = 1883
    EMQ_USE_SSL = False
