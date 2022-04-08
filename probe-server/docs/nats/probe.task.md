probe.task.*
============

任务相关。

## 数据结构

### ```[-target-]```

```
[
    // {-target:domain-}
    {
        "type": "domain",
        "rtype": str,
        "data": str
    },

    // {-target:domain_group-}
    {
        "type": "domain_group",
        "rtype": str,
        "domain_group_id": int
    }
]
```

### ```{-probe-data-}```

```
{
    "dns_servers": [ array of str ]
}
```

### ```{-answer-section-}```

```
{
    'name': 'www.asdasd.com.', 
    'ttl': 61, 
    'rdclass': 'IN', 
    'rdtype': 'A', 
    'result': '121.254.178.253'
}
```

### ```{-authority-section-}```

```
{
    'name': 'www.asdasd.com.', 
    'ttl': 61, 
    'rdclass': 'IN', 
    'rdtype': 'A', 
    'result': '121.254.178.253'
}
```

### ```{-additional-section-}```

```
{
    'name': 'www.asdasd.com.', 
    'ttl': 61, 
    'rdclass': 'IN', 
    'rdtype': 'A', 
    'result': '121.254.178.253'
}
```


## Node -> Python

### probe.task.dns_result.one_shoot

发送一个一次性的->域名查询解析结果<-任务，等待返回。

#### send

```
{
    "probe_data": {-probe-data-},
    "target": {-target:domain-},
    "group_id": int //拨测组id
    "regions": [
        //按照区域搜索拨测端
        [country_id, province_id, city_id, carrier], ...
    ] 
    "resp_timeout": int //指定等待超时,缺省3s
}
```

#### return

```
{
    "results": [ array of str ]
}
```

### probe.task.dns_result.one_shoot.verbose

发送一个一次性的->域名查询解析结果<-任务，等待返回。

复杂版本

#### send

```
{
    "probe_data": {-probe-data-},
    "target": [{-target:domain-}],
    "group_id": int //拨测组id
    "regions": [
        //按照区域搜索拨测端
        [country_id, province_id, city_id, carrier], ...
    ] 
    "resp_timeout": int //指定等待超时,缺省3s
}
```

#### return

```
{
    "results": [
        {
            "domain": str  //域名
            "delay": float  //延迟
            "dns_response_status": str,  //返回码
            "dns_server": str  //解析所用的dns服务器
            "device": {
                # 拨测端设备信息
                "country": "86",
                "province": "440000",
                "city": "440400",
                "carrier": "电信"
            },
            "answer_section": [{-answer-section-}],
            "authority_section": [{-authority-section-}],
            "additional_section": [{-additional-section-}]
        }
    ]
}
```

## Python -> Node

### probe.task.get

获取全部任务

#### send

-

#### return

```
[
    {
        "task_id": str,
        "type": str-任务类型,
        "service_type": str-任务子类型,
        "cycle": int-间隔时间（单位秒，0表示只执行一次）
        "probe_data": {-probe-data-},
        "target": [{-target-}],
        "status": int // 0暂停 1启用
        "group_id": int //拨测组id,
        "uid":
        "gid":
    }
]
```
