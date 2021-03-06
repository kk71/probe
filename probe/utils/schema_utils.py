# Author: kk.Fang(fkfkbill@gmail.com)

import json
from typing import List

import arrow
from schema import And, Use, Optional as scm_optional, Schema, SchemaError,\
    Or as scm_or

from utils import const

scm_and = And

__all__ = [
    "Schema",
    "scm_str",
    "scm_int",
    "scm_gt0_int",
    "scm_float",
    "scm_num",
    "scm_unempty_str",
    "scm_str_with_no_lr_spaces",
    "scm_something_split_str",
    "scm_dot_split_str",
    "scm_dot_split_int",
    "scm_subset_of_choices",
    "scm_one_of_choices",
    "scm_date",
    "scm_date_end",
    "scm_datetime",
    "scm_bool",
    "scm_optional",
    "scm_or",
    "scm_and",
    "scm_raise_error",
    "scm_empty_as_optional",
    "scm_deduplicated_list_of_dict",
    "scm_json"
]


def auto_num(x):
    if isinstance(x, (int, float)):
        return x
    elif isinstance(x, str):
        if "." in x:
            return float(x)
        else:
            return int(x)
    else:
        raise Exception("not a number.")


def scm_raise_error(*args, **kwargs):
    """便于在lambda里唤起SchemaError"""
    raise SchemaError(*args, **kwargs)


def scm_empty_as_optional(scm_validator, empty_contents=("",), ret_when_empty=None):
    """
    允许传入空字符串来表达'不传'的概念
    :param scm_validator: 原有的验证
    :param empty_contents: 定义什么是空？
    :param ret_when_empty: 如果传入"空"，那么将返回什么
    :return:
    """
    return scm_or(
        scm_validator,
        Use(lambda x: ret_when_empty if x in empty_contents else scm_raise_error())
    )


# for string
scm_str = Use(str)
scm_unempty_str = And(scm_str, lambda x: len(x.strip()) > 0)
scm_str_with_no_lr_spaces = And(scm_str, Use(lambda x: x.strip()))
scm_something_split_str = lambda splitter, p=scm_str: \
    Use(lambda x: [p.validate(i.strip()) for i in x.split(splitter) if i.strip()])
scm_dot_split_str = scm_something_split_str(",", scm_unempty_str)
scm_subset_of_choices = lambda choices: lambda subset: set(subset).issubset(set(choices))
scm_one_of_choices = lambda choices: lambda x: x in choices
scm_json = lambda x: And(scm_str, Use(lambda v: Schema(x).validate(json.loads(v))))

# for integer and float
scm_float = Use(float)
scm_int = Use(int)
scm_num = Use(auto_num)
scm_gt0_int = And(scm_int, lambda x: x > 0)
scm_dot_split_int = scm_something_split_str(",", scm_int)

# for bool(real boolean or string transformed)
scm_bool = Use(lambda x: x not in (0, "0", False))

# for date and time
scm_datetime = Use(lambda x: arrow.get(x, const.COMMON_DATETIME_FORMAT).datetime)
scm_date = Use(lambda x: arrow.get(x, const.COMMON_DATE_FORMAT).date())
scm_date_end = Use(lambda x: arrow.get(x, const.COMMON_DATE_FORMAT).shift(days=+1).date())


def _scm_deduplicated_list_of_dict(list_of_dict: List[dict]):
    a = []
    for i in list_of_dict:
        if i not in a:
            a.append(i)
    return a


# 元素为dict的list去重
scm_deduplicated_list_of_dict = Use(_scm_deduplicated_list_of_dict)
