# Author: kk.Fang(fkfkbill@gmail.com)
__all__ = [
    "timing"
]

import time
from functools import wraps
from typing import Optional

from loguru._logger import Logger

from settings import Setting


def func_info(method):
    return f"{method.__name__} in {method.__code__.co_filename}:" \
           f"{method.__code__.co_firstlineno}"


def timing(
        enabled: bool = Setting.TIMING_ENABLED,
        threshold: float = Setting.TIMING_THRESHOLD,
        named_logger: Optional[Logger] = None
):
    """
    函数计时
    :param enabled: 是否启用当前的计时器
    :param threshold: 计时器打印日志的阈值
    :param named_logger: 是否使用指定命名的loguru.logger记录，或者默认使用print
    :return:
    """
    echo = print
    if named_logger:
        echo = named_logger.info

    def timing_wrap(method):

        @wraps(method)
        def timed(*args, **kwargs):

            tiks = []

            ts = time.time()

            def tik(msg: str = None):
                """在过程中掐一下时间"""
                tt = time.time()
                s = f"{round(tt - ts, 3)}"
                if msg:
                    s += " " + str(msg)
                if enabled:
                    tiks.append(s)
                else:
                    # if the timing is disabled, the tik also should be printed.
                    echo(s)

            timed.tik = tik

            result = method(*args, **kwargs)
            te = time.time()
            t_rst = round(te - ts, 3)

            if enabled and t_rst >= threshold:
                leading_spaces = "\n      * "
                tiks_formatted = leading_spaces + leading_spaces.join(tiks) if tiks else ""
                r = f"""
      {func_info(method)}
        args: {args}, kwargs: {kwargs}{tiks_formatted}
        {t_rst} seconds total
    """
                echo(r)

            return result

        return timed

    return timing_wrap
