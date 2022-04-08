# Author: kk.Fang(fkfkbill@gmail.com)

from collections import defaultdict

from utils.ensured_dict import *
from models.elasticsearch import *
from .base import *
from ..models import *


class ESResultDispatchByIP(BaseESInnerDoc):
    """结果调度"""

    # 当前解析得到的IP
    ip = BaseESIPLocation()

    # 该域名下的全部资源使用该IP的访问时间总和
    seconds_sum = ESFloat()


class ESDNSDispatchByDNSServer(BaseESInnerDoc):
    """dns调度"""

    # 当前使用的dns服务器
    dns_server = ESKeyword()

    # 该域名下的全部资源使用该dns解析得到的IP的访问时间中最慢的时间
    seconds_slowest = ESFloat()


class ESInnerDocSpeedUpBestChoice(BaseESInnerDoc):
    """优选结果+理由"""

    domain = ESKeyword()

    # 以下字段根据dispatchType区分
    # 结果调度
    ip = BaseESIPLocation()
    ip_dns_server = ESNested()  # 结果调度的IP的dns解析来源
    by_ip = ESNested(ESResultDispatchByIP)

    # dns调度
    dns_server = ESKeyword()
    by_dns_server = ESNested(ESDNSDispatchByDNSServer)


class ESDocPageSpeedUpStatistics(BaseESStatisticsDoc):
    """页面提速分析的统计结果"""

    # 被分析的首页
    main_url = ESKeyword()

    # 优选结果
    best_choices = ESNested(ESInnerDocSpeedUpBestChoice)

    class Index:
        name = "page-speedup-*"
        settings = {}


class ProbeDataStatisticsTaskPageSpeedUp(ProbeDataStatistics):
    # 所有可选的调度方式
    ALL_DISPATCH_TYPE = (
        DISPATCH_TYPE_RESULT := "0",  # 结果调度（强制调度）
        DISPATCH_TYPE_DNS := "1"  # dns调度（代理调度）
    )

    # 调度方式
    dispatchType = EDV(DISPATCH_TYPE_RESULT)


@StatisticsTask.need_collect()
class StatisticsTaskPageSpeedUp(StatisticsTask):
    """页面分析提速统计任务"""

    TASK_TYPE = TaskType("resource", "pageSpeedUp")

    PROBE_DATA = ProbeDataStatisticsTaskPageSpeedUp

    def __init__(self, **kwargs):
        super(StatisticsTaskPageSpeedUp, self).__init__(**kwargs)

        # 存留一个probedata的doc，用于填充其中所需的数据到统计doc
        self.one_probedata_doc = None

        # 保存所有用到的task_probing_id, 后续需要记录到统计表
        self.referenced_task_probing_id = set()

        # domain:ip:[(seconds, url, dns_server), ...]
        # 记录每个域名下不同的url的访问时间
        self.url_results = defaultdict(lambda: defaultdict(list))

        # ip: {dns set}
        self.ip_dns_server = defaultdict(set)

    def set_all_records(self):
        """
        不考虑分析方式，仅仅先把所有数据按照格式放入结构
        :return:
        """
        # 把结果都放入url_results
        for one_probing_id in self.get_task_probing_id():
            r = ESProbeData.search().query("term", task_probing_id=one_probing_id)
            for i in r.scan():
                self.one_probedata_doc = i
                ihi = i.http_info
                self.url_results[ihi.domain][ihi.ip].append((
                    ihi.response_time, ihi.url, ihi.dns_server))
                self.ip_dns_server[ihi.ip].add(ihi.dns_server)
                self.referenced_task_probing_id.add(i.task_probing_id)

    def make_doc(self):
        return ESDocPageSpeedUpStatistics(
            task_type=self.one_probedata_doc.task_type,
            task_id=self.one_probedata_doc.task_id,
            referenced_task_probing_id=list(self.referenced_task_probing_id),
            client_id=self.one_probedata_doc.client_id,
            client_ip=self.one_probedata_doc.client_ip,
            probe_task_status=self.one_probedata_doc.probe_task_status,
            main_url=self.target[0]["data"],
            task_statistics_id=self.task_statistics_id
        )

    def by_dns(self):
        """
        按照dns调度方式
        根据给定的dns，逐个dns去解析全部域名，找出各域名下响应最慢的那个URL-IP的响应时间，
        以这个响应时间作为该dns的时间，然后找到所有dns的响应最慢时间里最快的，
        即该dns是最优选择
        :return:
        """
        # domain: dns_server: (seconds, ...)
        domain_dns_server_seconds = defaultdict(lambda: defaultdict(list))
        # 对url结果排序，然后选取同个url下，不同的ip访问速度最快的ip，计入domain_results
        for domain, i1 in self.url_results.items():
            for ip, i2 in i1.items():
                for seconds, _, dns_server in i2:
                    domain_dns_server_seconds[domain][dns_server].append(seconds)

        doc = self.make_doc()
        for domain, i1 in domain_dns_server_seconds.items():
            slowest_seconds_dns_server = []
            for dns_server, list_of_seconds in i1.items():
                list_of_seconds.sort(reverse=True)  # 按照响应时间倒序
                slowest_seconds_dns_server.append((list_of_seconds[0], dns_server))
            slowest_seconds_dns_server.sort()
            best_choice = ESInnerDocSpeedUpBestChoice(
                domain=domain,
                dns_server=slowest_seconds_dns_server[0][1]
            )
            for i in slowest_seconds_dns_server:
                best_choice.by_dns_server.append(ESDNSDispatchByDNSServer(
                    dns_server=i[1],
                    seconds_slowest=i[0]
                ))
            doc.best_choices.append(best_choice)
        # 写入es
        doc.save()

    def by_result(self):
        """
        按照结果调度的方式
        按照给定dns_server列表，解析出各个域名的全部IP，
        然后计算各个域名下，所有URL在各IP的情况下的访问时间总和
        取访问时间最快的IP，作为这个域名的优选IP
        :return:
        """
        # domain:[(seconds_sum, ip), ...]
        # 选取每个域名最快的ip(针对该域名下的全部URL)
        domain_ip_seconds_sum = defaultdict(list)

        # 对url结果排序，然后选取同个url下，不同的ip访问速度最快的ip，计入domain_results
        for domain, i1 in self.url_results.items():
            for ip, i2 in i1.items():
                seconds_sum = sum([j[0] for j in i2 if j and j[0]])
                domain_ip_seconds_sum[domain].append(
                    (seconds_sum, ip)
                )

        # 对domain的结果选取出现次数最多的，构造best_choice
        doc = self.make_doc()
        for domain, seconds_sum_ip_pairs in domain_ip_seconds_sum.items():
            if not seconds_sum_ip_pairs:
                continue
            seconds_sum_ip_pairs.sort()
            fastest_ip: str = seconds_sum_ip_pairs[0][1]
            best_choice = ESInnerDocSpeedUpBestChoice(
                domain=domain,
                ip=BaseESIPLocation.ipdb_to_location(fastest_ip)
            )
            for pair in seconds_sum_ip_pairs:
                the_ip = pair[1]
                best_choice.by_ip.append(ESResultDispatchByIP(
                    ip=BaseESIPLocation.ipdb_to_location(the_ip),
                    seconds_sum=pair[0]
                ))
            best_choice.ip_dns_server = [
                BaseESIPLocation.ipdb_to_location(dns_server)
                for dns_server in self.ip_dns_server.get(fastest_ip)
            ]
            doc.best_choices.append(best_choice)
        # 写入es
        doc.save()

    def _fire(self, **kwargs):
        self.set_all_records()
        if self.probe_data["dispatchType"] == \
                ProbeDataStatisticsTaskPageSpeedUp.DISPATCH_TYPE_RESULT:
            return self.by_result()
        if self.probe_data["dispatchType"] == \
                ProbeDataStatisticsTaskPageSpeedUp.DISPATCH_TYPE_DNS:
            return self.by_dns()
        else:
            assert 0
