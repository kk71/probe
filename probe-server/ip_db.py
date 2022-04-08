# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "IPDB"
]

import ipdb

from core.cached import *


class IPDB(BaseCached):
    """存放IPDB的缓存"""

    CACHED_DATA = dict()

    DB = ipdb.City("assets/IPIP.ipdb")

    @classmethod
    def get(cls, ip: str) -> dict:
        if ip not in cls.CACHED_DATA.keys():
            cls.CACHED_DATA[ip] = cls.DB.find_map(ip, "CN")
        # 特殊情况的IP，会查询到region_name为"中国"，这里把这种情况的region_name设置为""
        # 譬如： 202.97.33.181
        if cls.CACHED_DATA[ip].get("region_name", None) == "中国":
            cls.CACHED_DATA[ip]["region_name"] = ""
        return cls.CACHED_DATA[ip]
