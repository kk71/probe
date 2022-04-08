# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseESIPLocation",
    "ESProbeData",
    "ESProbeDataHttpInfo",
    "ESProbeDataRoute",
    "BaseESStatisticsDoc",
    "ESIPLocationException"
]

import uuid

import arrow
from elasticsearch_dsl import GeoPoint as ESGeoPoint

from settings import Setting
from ip_db import *
from models.elasticsearch import *
from models.redis import RedisTaskStatisticsIdLatest


class ESIPLocationException(Exception):
    pass


class BaseESIPLocation(BaseESInnerDoc):
    """内嵌的地址信息"""

    country = ESKeyword()
    country_id = ESKeyword()
    province = ESKeyword()
    province_id = ESKeyword()
    city = ESKeyword()
    city_id = ESKeyword()
    carrier = ESKeyword()

    # 地理位置唯一id
    location_id = ESKeyword()

    gps = ESGeoPoint()
    ip = ESKeyword()

    @classmethod
    def ipdb_to_location(cls, ip, strict: bool = False) -> "BaseESIPLocation":
        """
        制作一个地理信息
        请注意！！！务必使用try-exception，
        特殊异常的地址信息会抛出异常，提示不要使用
        :param ip:
        :param strict: 异常的信息是否抛出错误
        :return:
        """
        ipdb_info = IPDB.get(ip)
        ret = cls()
        ret.ip = ip
        ret.country_id = ipdb_info["idd_code"]
        ret.country = ipdb_info["country_name"]
        ret.province_id = ipdb_info["china_admin_code"][:2] + "0000"
        ret.province = ipdb_info["region_name"]
        ret.city_id = ipdb_info["china_admin_code"]
        ret.city = ipdb_info["city_name"]
        ret.carrier = ipdb_info["isp_domain"]
        ret.set_location_id()
        ret.gps = {
            "lat": ipdb_info["latitude"],
            "lon": ipdb_info["longitude"]
        }

        if strict:
            # 各种判断
            if ret.country in ("114DNS.COM",):
                raise ESIPLocationException(f"{ret.country=}")

        return ret

    def set_location_id(self):
        """
        country_id, province_id, city_id, carrier拼接文本
        """
        self.location_id = f"{self.country_id}-" \
                           f"{self.province_id}-{self.city_id}-{self.carrier}"

    def __init__(self, *args, **kwargs):
        super(BaseESIPLocation, self).__init__(*args, **kwargs)
        if not self.location_id:
            self.set_location_id()


class ESProbeDataHttpInfo(BaseESInnerDoc):
    """resource-pageSpeedup http拨测结果"""

    url = ESKeyword()
    domain = ESKeyword()
    dns_server = ESKeyword()
    ip = ESKeyword()
    response_time = ESKeyword()
    create_time = ESDate()
    probe_task_status = ESKeyword()


class ESProbeDataRoute(BaseESInnerDoc):
    """network-traceroute 每一次hop"""

    packet_loss = ESKeyword()
    max_rtt = ESFloat()
    min_rtt = ESFloat()
    distance = ESInteger()
    packets_sent = ESInteger()
    avg_rtt = ESFloat()
    packets_received = ESInteger()
    ip = ESKeyword()


class ESProbeData(BaseESDoc):
    """
    拨测结果字段
    TODO 请注意这个索引下的数据只有java模块可以改。这里只提供读取
         拨测结果数据是全部类型统一用一个索引的，因此新需求来的时候只加新字段，轻易不要修改原有的
    """
    task_type = ESKeyword()
    task_id = ESKeyword()
    task_probing_id = ESKeyword()
    client_id = ESKeyword()
    client_ip = ESObject(BaseESIPLocation)
    client_version = ESKeyword()
    create_time = ESDate()
    probe_task_status = ESKeyword()

    # resource-pageSpeedup
    http_info = ESNested(ESProbeDataHttpInfo)

    # network-traceroute
    ip = ESKeyword()
    routes = ESNested(ESProbeDataRoute)
    last_route = ESObject(ESProbeDataRoute)

    # dns
    domain = ESKeyword()
    dns_server_ip = ESObject(BaseESIPLocation)
    dns_response_status = ESKeyword()
    answer = ESNested(BaseESIPLocation)

    class Index:
        name = "probedata-*"
        settings = {}


class BaseESStatisticsDoc(BaseESDoc):
    """基础的es统计字段"""

    # 统计id
    task_statistics_id = ESKeyword()

    # 任务类型
    task_type = ESKeyword()

    # 任务id
    task_id = ESKeyword()

    # 本次统计涉及的拨测id
    referenced_task_probing_id = ESKeyword()

    # 拨测端id
    client_id = ESKeyword()

    # 拨测端信息
    client_ip = ESObject(BaseESIPLocation)

    # 拨测任务结果
    probe_task_status = ESKeyword()

    # 统计时间
    create_time = ESDate()

    def save(self,  **kwargs):
        if not self.task_statistics_id:
            self.task_statistics_id = uuid.uuid4().hex
        if not self.create_time:
            self.create_time = arrow.now().datetime
        kwargs['index'] = self.Index.name.replace(
            "*",
            self._get_index_date_postfix()
        )
        r = super(BaseESStatisticsDoc, self).save(**kwargs)
        RedisTaskStatisticsIdLatest.redis_db_instance.set(
            self.task_id,
            self.task_statistics_id,
            ex=Setting.STATISTICS_LAST_RECORD_ID_EXPIRE
        )
        return r

    def _get_index_date_postfix(self) -> str:
        return self.create_time.strftime('%Y.%m.%d')
