# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "CoreSetting",
    "SettingValueUnset"
]

from os import environ
from typing import Any, Callable, Tuple

from .self_collecting_class import *


class SettingValueUnset:
    """设置值未配置的占位符"""
    pass


class CoreSetting(SelfCollectingFramework):
    # 指定配置的tag，在启动的时候选用对应的配置
    _tag = None

    @classmethod
    def shorten(cls, s, length_max: int = 30):
        if not isinstance(s, str):
            s = str(s)
        if s != s[:length_max]:
            s = s[:length_max] + " ... "
        return s

    @classmethod
    def need_collect(cls):
        def inner(model):
            assert issubclass(model, cls)
            for k in dir(model):
                if not k.startswith("_"):
                    # 检查需要替换的值是否在子类里替换掉
                    v = getattr(model, k)
                    if v is SettingValueUnset:
                        raise Exception(
                            f"BaseSetting values not overridden in sub setting: {k}")
            if model not in cls.COLLECTED:
                cls.COLLECTED.append(model)
            return model

        return inner

    @classmethod
    def from_env(cls,
                 name: str,
                 default: Any = None,
                 set_type: Callable = None) -> Any:
        """
        从系统环境变量中获取某个配置的值
        :param name:
        :param default: 缺省值
        :param set_type: 值的预处理，或者用于转换成特定的数据类型
                        注意，如果返回缺省值，则不会使用set_type去转换
        :return:
        """
        v = environ.get(name, None)
        if v is None:
            v = default
        elif set_type:
            v = set_type(v)
        else:
            pass
        return v

    @classmethod
    def print(cls):
        """打印配置的所有值"""
        raise NotImplementedError

    @classmethod
    def all_setting_keys(cls) -> Tuple[str]:
        """返回全部配置的key"""
        keys = []
        for k in dir(cls):
            if k.startswith("_"):
                continue
            if not k.isupper():
                continue
            if k in ("COLLECTED", "PATH_TO_IMPORT",
                     "RELATIVE_IMPORT_TOP_PATH_PREFIX", "ALL_SUB_CLASSES",
                     "META_METHOD", "BASE_CLASS", "SETTING_FILE_DIR",
                     "FAIL_CONTINUE", "FAIL_PRINT_TRACE"):
                continue
            keys.append(k)
        return tuple(set(keys))
