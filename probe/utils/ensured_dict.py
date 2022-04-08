# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "EnsuredDict",
    "EnsuredDictValue",
    "EDV"
]

import copy
from typing import Dict


class EnsuredDictValue:
    """缺省值，不填则默认使用None"""

    def __init__(self, default_value=None, **kwargs):
        self.default_value = default_value


EDV = EnsuredDictValue


class EnsuredDictMeta(type):

    def __init__(cls, name, bases, attrs: Dict):
        super().__init__(name, bases, attrs)
        ENSURED_DICT = {}
        for b in bases:
            if getattr(b, "ENSURED_DICT", {}):
                ENSURED_DICT.update(b.ENSURED_DICT)
        for k, v in attrs.items():
            if isinstance(v, EnsuredDictValue):
                if not callable(v.default_value):
                    v = v.default_value
                    if v is not None and not isinstance(v, (str, int, float, tuple)):
                        # be careful of those changeable objects
                        v = copy.deepcopy(v)
                ENSURED_DICT[k] = v
        cls.ENSURED_DICT = ENSURED_DICT


class EnsuredDict(dict, metaclass=EnsuredDictMeta):
    """一个保证字段的字典"""

    # 可变对象是否需要深拷贝
    CHANGEABLE_VALUE_NEED_DEEPCOPY: bool = True

    def __init__(self, *args, **kwargs):
        super(EnsuredDict, self).__init__(*args, **kwargs)
        for k, v in self.ENSURED_DICT.items():
            if isinstance(v, EnsuredDictValue):
                v = v.default_value
            if callable(v):
                # ony accept callable with no input arguments
                v = v()
            if v is not None and not isinstance(v, (str, int, float, tuple)):
                if self.CHANGEABLE_VALUE_NEED_DEEPCOPY:
                    v = copy.deepcopy(v)
            self[k] = self.get(k, v)
