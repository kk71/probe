task.statistics.*
=================

拨测服务端发出来的拨测任务的相关信息

## 数据类型

### {-ip-location-} IP以及地理运营商信息

```
{
        "location_id": "86-440000-440400-电信",
        "country": "中国",
        "carrier": "电信",
        "province": "广东",
        "city": "珠海",
        "province_id": "440000",
        "gps": {
            "lon": 113.55681,
            "lat": 22.277
        },
        "country_id": "86",
        "city_id": "440400"
}
```

## Python -> Node

### task.statistics.dns_prefer.result

dns_prefer任务类型的分析结果。每次有新结果的时候都会发送一次。

数据结构与es的结构一直。

#### send

-

#### return

```
{
    "domain": "www.yamu.com",
    "task_id": "15dc7720-58fa-4004-958c-2f99ad883849",
    "task_type": "dns-dnsPrefer",
    "referenced_task_probing_id": "d1a7f34e69884328b3386ea1c38a8349",
    "client_id": "ef864b52e37b4cb7932daedb138414ad",
    "client_ip": {-ip-location-},
    "probe_task_status": "0",
    "dns_ip_group": [
        {
            "dns": {
                "location_id": "-0000--阿里云",
                "ip": "223.6.6.6",
                "country_id": "",
                "country": "ALIDNS.COM",
                "province_id": "0000",
                "province": "ALIDNS.COM",
                "city_id": "",
                "city": "",
                "carrier": "阿里云",
                "gps": {
                    "lat": "0",
                    "lon": "0"
                }
            },
            "delay": 7.182598114013672,
            "dns_response_status": "NOERROR",
            "ips": [
                {
                    "ip": "121.40.108.103",
                    "outnet": true
                }
            ]
        }, ...
    ],
    "task_statistics_id": "33e2095fd0e4462ea90f80bad403f65b",
    "create_time": "2021-10-08 15:21:25"
}
```
