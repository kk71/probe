# Author: kk.Fang(fkfkbill@gmail.com)

from collections import defaultdict

from models.elasticsearch import *
from ..models import *
from .base import *
from utils.dt_utils import *


class TracerouteRouteSummary(BaseESInnerDoc):
    """汇总的route"""

    # 当前ttl
    distance = ESKeyword()

    # 当前ttl出现过的全部ip信息
    location = ESNested(BaseESIPLocation)

    # 一共发送包累计
    packets_sent = ESInteger()

    # 一共接收包累计
    packets_received = ESInteger()

    # 丢包率
    packet_loss = ESFloat()

    max_rtt = ESFloat()

    avg_rtt = ESFloat()

    min_rtt = ESFloat()

    # 最后一次（也就是traceroute的某个route）的延迟
    last_rtt = ESFloat()

    # 标准差
    standard_deviation = ESFloat()


class ESDocTracerouteSummaryStatistics(BaseESStatisticsDoc):
    """
    traceroute的汇总信息

    注意：汇总按照 task_id:IP:location_id做唯一标识，新数据写入之前，先删掉旧的
    """
    # 本次统计的本地时间日期文本
    # datetime是排序用，而且datetime是utc，不易于展示。
    # 请注意统计按照天为单位，虽然可以统计多次，但是每次只保留当天的数据
    date = ESText(fields={'keyword': ESKeyword()})

    # 目标ip
    ip = ESKeyword()

    # 汇总的routes
    routes = ESNested(TracerouteRouteSummary)

    class Index:
        name = "traceroute-summary-*"
        settings = {}

    def save(self,  **kwargs):
        # 删除原始已存在的全部统计数据
        r = self.search(). \
            query("term", task_id__keyword=self.task_id). \
            query("term", ip__keyword=self.ip).\
            query("term", date=self.date).\
            query("term", client_id__keyword=self.client_id)
        r.delete()
        # 写入
        super(ESDocTracerouteSummaryStatistics, self).save(**kwargs)


@StatisticsTask.need_collect()
class StatisticsTaskNetworkTraceroute(StatisticsTask):
    """页面分析提速统计任务"""

    TASK_TYPE = TaskType("network", "traceroute")

    def _fire(self, **kwargs):

        # 当前utc，用于标识本次分析的时间
        utcnow = arrow.utcnow()
        date_local = d_to_str(arrow.now())

        # 所有需要统计和的keys
        KEYS_SUM_UP = (
            "packets_received",
            "packets_sent",
        )

        # client_id: target_ip: distance: route
        routes = defaultdict(lambda: defaultdict(lambda: defaultdict(TracerouteRouteSummary)))

        # client_id: target_ip: distance: {ip set}
        distance_ips = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

        # client_id: target_ip: sample_probe_data_doc
        ip_probe_data_doc = defaultdict(dict)

        # TODO 这里界定统计哪些信息。目前统计的是从当日本地时间的0点开始至现在的信息，
        #      也就是说，永远只统计今天的信息
        #      请注意，这个时间是本地时间的0点至现在时间！
        r = ESProbeData.search().query(
            "range",
            create_time={
                "gt": utcnow.shift(hours=+8).replace(hour=0, minute=0, second=0).datetime
            }
        ).query("term", task_id=self.task_id).sort("create_time")
        # 加上了按照写入es的时间排序

        for probe_data_doc in r.scan():

            # 存放一个指向当前拨测目标ip的probe_data的最后一个doc
            # 一方面用于获取拨测端信息，另一方面用于获取最后一次traceroute的延迟
            ip_probe_data_doc[probe_data_doc.client_id][probe_data_doc.ip] = probe_data_doc

            for i, probe_data_route in enumerate(probe_data_doc.routes):

                current_distance = i + 1

                current_route = routes[probe_data_doc.client_id][probe_data_doc.ip][current_distance]
                current_route.distance = current_distance

                distance_ips[probe_data_doc.client_id][probe_data_doc.ip][current_distance].add(probe_data_route.ip)

                # 统计需要累加的key
                for k in KEYS_SUM_UP:
                    original_v = getattr(current_route, k)
                    append_v = getattr(probe_data_route, k)
                    if not original_v:
                        original_v = 0
                    if not append_v:
                        append_v = 0
                    setattr(current_route, k, original_v + append_v)

                # max_rtt, min_rtt
                if current_route.max_rtt:
                    current_route.max_rtt = max((current_route.max_rtt, probe_data_route.max_rtt))
                else:
                    current_route.max_rtt = probe_data_route.max_rtt
                if current_route.min_rtt:
                    current_route.min_rtt = min((current_route.min_rtt, probe_data_route.min_rtt))
                else:
                    current_route.min_rtt = probe_data_route.min_rtt

                # avg_rtt
                if not current_route.avg_rtt:
                    current_route.avg_rtt = []
                current_route.avg_rtt.append(probe_data_route.avg_rtt)

                # last_rtt
                current_route.last_rtt = probe_data_route.avg_rtt

        for client_id, t in routes.items():

            for target_ip, tt in t.items():

                # 当前拨测端-目标IP的traceroute的最后一次拨测
                last_doc_of_current_traceroute = ip_probe_data_doc[client_id][target_ip]

                for distance, route in tt.items():

                    for ip in distance_ips[client_id][target_ip][distance]:
                        route.location.append(BaseESIPLocation.ipdb_to_location(ip))

                    route.packet_loss = float(route.packets_sent - route.packets_received) / float(route.packets_sent)

                    # 记录一下全部的avg_rtt列表
                    route_all_avg_rtt = route.avg_rtt

                    route.avg_rtt = sum(route.avg_rtt) / float(len(route_all_avg_rtt))

                    route.standard_deviation = pow(
                        sum([pow(i - route.avg_rtt, 2) for i in route_all_avg_rtt]) / float(len(route_all_avg_rtt)),
                        0.5
                    )

                r = ESDocTracerouteSummaryStatistics(
                    task_type=str(self.task_type),
                    task_id=self.task_id,
                    date=date_local,
                    ip=target_ip,
                    client_ip=last_doc_of_current_traceroute.client_ip,
                    client_id=client_id,
                    routes=sorted(list(tt.values()), key=lambda x: x.distance),
                    task_statistics_id=self.task_statistics_id
                )
                r.save()
