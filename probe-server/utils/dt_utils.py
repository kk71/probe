# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "arrow",
    "date",
    "datetime",
    "timedelta",
    "COMMON_DATE_FORMAT",
    "COMMON_DATE_FORMAT_COMPACT",
    "COMMON_TIME_FORMAT",
    "COMMON_DATETIME_FORMAT",
    "dt_to_str",
    "d_to_str",
    "t_to_str",
    "str_to_dt",
    "str_to_d",
    "str_to_t"
]

from typing import Union, Optional

import arrow
from datetime import date, datetime, timedelta, time

from utils.const import \
    COMMON_DATETIME_FORMAT, COMMON_DATE_FORMAT, COMMON_TIME_FORMAT,\
    COMMON_DATE_FORMAT_COMPACT


def dt_to_str(dt: Union[datetime, arrow.Arrow, list, tuple, dict]) -> Union[str, list, dict]:
    if isinstance(dt, (datetime, arrow.Arrow)):
        return arrow.get(dt).format(fmt=COMMON_DATETIME_FORMAT)

    elif isinstance(dt, (list, tuple)):
        return [dt_to_str(i) for i in dt]

    elif isinstance(dt, dict):
        return {k: dt_to_str(v) for k, v in dt.items()}

    else:
        return dt


def d_to_str(
        d: Union[datetime, arrow.Arrow, date],
        fmt=COMMON_DATE_FORMAT) -> Optional[str]:
    if not d:
        return None
    return arrow.get(d).format(fmt=fmt)


def t_to_str(t: time, fmt=COMMON_TIME_FORMAT) -> Optional[str]:
    if not t:
        return None
    return arrow.now().replace(
        hour=t.hour, minute=t.minute, second=t.second).format(fmt=fmt)


def str_to_dt(
        s: str,
        allow_none_to_none: bool = True) -> Optional[datetime]:
    if s is None and allow_none_to_none:
        return None
    return arrow.get(s).datetime


def str_to_d(
        s: str,
        allow_none_to_none: bool = True) -> Optional[date]:
    if s is None and allow_none_to_none:
        return None
    return arrow.get(s).date()


def str_to_t(
        s: str,
        allow_none_to_none: bool = True,
        fmt=COMMON_TIME_FORMAT) -> Optional[time]:
    if s is None and allow_none_to_none:
        return None
    return arrow.get(s, [fmt]).time()
