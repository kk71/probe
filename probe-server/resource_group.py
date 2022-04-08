# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "CachedDomainGroup",
    "CachedAddressGroup"
]

import json
import hashlib
from typing import DefaultDict
from collections import defaultdict

from utils.schema_utils import *
from cached import *
from mq.nats import *


class ResourceGroup(set):
    """
    带有hash的资源列表。
    资源可以是IP，域名，URL等
    TODO 请注意，hash计算仅在域名列表产生的时候进行，意味着如果你修改了这个列表，需要手动重新计算！
    """

    def __init__(self, *args, name: str, **kwargs):
        super(ResourceGroup, self).__init__(*args, **kwargs)
        self.hash: str = None
        self.name = name
        self.calc_hash()

    def calc_hash(self) -> str:
        """
        重新计算hash
        :return: str
        """
        sorted_items = list(self)
        sorted_items.sort()
        self.hash = hashlib.md5(json.dumps(sorted_items).encode("utf-8")).hexdigest()
        return self.hash


class NATSReqDomainGroup(NATSRequestHandler):
    """获取域名分组"""

    SUBJECT = "probe.domain_group.get"

    @classmethod
    def response_schema(cls):
        return Schema([
            {
                "id": scm_int,
                "name": scm_unempty_str,
                "domains": [scm_unempty_str]
            }
        ], ignore_extra_keys=True)


class CachedDomainGroup(Cached):
    """域名分组"""

    CACHED_DATA: DefaultDict[
        int,  # 域名列表id
        ResourceGroup  # set{域名}
    ] = None

    # 发送接受组信息的nats
    NATS_HANDLER = None

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        new_data = defaultdict(ResourceGroup)
        ret = await cls.NATS_HANDLER.request(NATSReqDomainGroup)
        for a in ret:
            new_data[a["id"]] = ResourceGroup(a["domains"], name=a["name"])
        cls.CACHED_DATA = new_data  # THIS IS THREAD-SAFE

    @classmethod
    def get(cls, group_id: int) -> ResourceGroup:
        """查询某个域名分组"""
        return cls.CACHED_DATA[group_id]

    @classmethod
    async def content_on_update(cls, *args, **kwargs):
        await cls.content_initialize(nats_handler=cls.NATS_HANDLER)


class NATSReqAddressGroup(NATSRequestHandler):
    """获取地址分组"""

    SUBJECT = "probe.address_group.get"

    @classmethod
    def response_schema(cls):
        return Schema([
            {
                "id": scm_int,
                "name": scm_unempty_str,
                "addresses": [scm_unempty_str]
            }
        ], ignore_extra_keys=True)


class CachedAddressGroup(Cached):
    """地址分组"""

    CACHED_DATA: DefaultDict[
        int,  # 地址分组id
        ResourceGroup  # set{IP或者域名}
    ] = None

    # 发送接受组信息的nats
    NATS_HANDLER = None

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        new_data = defaultdict(ResourceGroup)
        ret = await cls.NATS_HANDLER.request(NATSReqAddressGroup)
        for a in ret:
            new_data[a["id"]] = ResourceGroup(a["addresses"], name=a["name"])
        cls.CACHED_DATA = new_data  # THIS IS THREAD-SAFE

    @classmethod
    def get(cls, group_id: int) -> ResourceGroup:
        """查询某个地址分组"""
        return cls.CACHED_DATA[group_id]

    @classmethod
    async def content_on_update(cls, *args, **kwargs):
        await cls.content_initialize(nats_handler=cls.NATS_HANDLER)


# ===========================================================================
# TODO the following url group is now unused and is served for future usage.
# ===========================================================================


class NATSReqURLGroup(NATSRequestHandler):
    """获取url分组"""

    SUBJECT = "probe.url_group.get"

    @classmethod
    def response_schema(cls):
        return Schema([
            {
                "id": scm_int,
                "name": scm_unempty_str,
                "urls": [scm_unempty_str]
            }
        ], ignore_extra_keys=True)


class CachedURLGroup(Cached):
    """url分组"""

    CACHED_DATA: DefaultDict[
        int,  # url分组id
        ResourceGroup  # set{url}
    ] = None

    # 发送接受组信息的nats
    NATS_HANDLER = None

    @classmethod
    async def content_initialize(cls, *args, **kwargs):
        new_data = defaultdict(ResourceGroup)
        ret = await cls.NATS_HANDLER.request(NATSReqURLGroup)
        for a in ret:
            new_data[a["id"]] = ResourceGroup(a["urls"], name=a["name"])
        cls.CACHED_DATA = new_data  # THIS IS THREAD-SAFE

    @classmethod
    def get(cls, group_id: int) -> ResourceGroup:
        """查询某个url分组"""
        return cls.CACHED_DATA[group_id]

    @classmethod
    async def content_on_update(cls, *args, **kwargs):
        await cls.content_initialize(nats_handler=cls.NATS_HANDLER)

