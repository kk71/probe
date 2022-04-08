__all__ = [
    "run_on_thread",
    "func_loop"
]

import time
import asyncio
import threading
import traceback
from functools import wraps
from typing import Callable

from utils.log_utils import get_bound_logger


def run_on_thread(f: Callable):
    """简单地让一个函数在新线程里跑"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        threading.Thread(
            target=f,
            name=f.__name__,
            args=args,
            kwargs=kwargs,
            daemon=None).start()

    return wrapped


# 一个专门给func_loop使用的logger
func_loop_logger = get_bound_logger("func_loop")


def func_loop(f: Callable):
    """确保一个函数退出后依旧再次执行，
    通常这个函数内有一个外层死循环，退出的原因是exceptions而非预期。"""
    s = 10
    if asyncio.iscoroutinefunction(f):
        @wraps(f)
        async def async_wrapped(*args, **kwargs):
            while True:
                try:
                    await f(*args, **kwargs)
                except:
                    func_loop_logger.error(traceback.format_exc())
                    func_loop_logger.warning(f"{f}: down and will be rerun after {s} seconds ...")
                await asyncio.sleep(s)
        return async_wrapped
    else:
        @wraps(f)
        def wrapped(*args, **kwargs):
            while True:
                try:
                    return f(*args, **kwargs)
                except:
                    func_loop_logger.error(traceback.format_exc())
                    func_loop_logger.warning(f"{f}: down and will be rerun after {s} seconds ...")
                time.sleep(s)
        return wrapped
