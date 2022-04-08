# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "Region"
]

import asyncio
from typing import DefaultDict, List, Iterable, Tuple
from collections import defaultdict

from cached import *
from .device import *
from .nats import *


class Region(Cached):
    """
    区域
    """

    NATS_HANDLER = SchedulerNATSHandler

    CACHED_DATA: DefaultDict[
        str,  # country
        DefaultDict[
            str,  # province
            DefaultDict[
                str,  # city
                DefaultDict[
                    str,  # carrier
                    List[str]  # list of client_id
                ]
            ]
        ]
    ] = None

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        """
        初始化可拨测的区域
        :param args:
        :param kwargs:
        :return:
        """
        while not InitializedDevice.initialized():
            await asyncio.sleep(1)  # 等待设备信息初始化

        new_data = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(list)
                )
            )
        )
        for client_id, the_device in InitializedDevice.CACHED_DATA.items():
            # TODO 请注意，区域的四个字段必须都不能为None，否则视为不允许拨测的区域
            if all([
                    the_device.country,
                    the_device.province,
                    the_device.city,
                    the_device.carrier]):
                new_data[str(the_device.country)] \
                    [str(the_device.province)] \
                    [str(the_device.city)] \
                    [the_device.carrier].append(client_id)
        cls.CACHED_DATA = new_data  # THIS IS THREAD-SAFE

    @classmethod
    def iter_region(cls, regions: Iterable[Tuple[str, str, str, str]] = ()):
        """
        一个循环region-client_id的生成器
        :return: iterator: ((country, province, city, carrier), [lit of client_id])
        """
        for c_country, d1 in cls.CACHED_DATA.items():
            for c_province, d2 in d1.items():
                for c_city, d3 in d2.items():
                    for c_carrier, client_ids in d3.items():
                        c_r = (c_country, c_province, c_city, c_carrier)
                        to_yield = c_r, client_ids
                        # 如果regions为空，则不匹配任何区域
                        for r in regions:
                            country, province, city, carrier = r
                            if province == city:
                                # 如果省和市相等（前端在选择直辖市的时候会默认给直辖市的省市代码相等）
                                r = country, province, None, carrier  # 处理直辖市
                            if all([
                                # 区域四个字段，如果为任何布尔否值，则表示这个字段不过滤(即认为是相等)
                                True if c_r[i] == r[i] or not r[i] else False
                                for i in range(4)
                            ]):
                                yield to_yield

    @classmethod
    def content_on_update(cls, *args, **kwargs):
        cls.content_initialize()
