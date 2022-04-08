probe.device.*
==============

设备相关。

考虑到设备将会是很大的一个量，每次都重复删掉写入不合理，因此维护一个差量更新。

## Python -> Node

### probe.device.post

添加设备

#### send

```
{
    ip:
    device_id:
    device_type:
    country:
    province:
    city:
    carrier:
    status:(str)
    schedule_time:
    task_limit:
    remark:
    mac_address:(str)
    client_version:(str)
    down_time:(datetime str)
}
```

#### return

-

### probe.device.put

修改设备

修改已有设备的信息，如果改设备没有同步到node，需要操作添加。

#### send

```
{
    ip:
    device_id:
    device_type:
    country:
    province:
    city:
    carrier:
    status:(str)
    schedule_time:
    task_limit:
    remark:
    mac_address:(str)
    client_version:(str)
    down_time:(datetime str)
}
```

#### return

-

### probe.device.delete

删除设备

#### send

```
{
    device_id:
}
```

#### return

-


## Node -> Python

### probe.fe.device.delete

页面操作设备删除

#### send

```
{
    device_id:
}
```

#### return

```
{
    "status": bool //是否成功
}
```

### probe.fe.device.put

页面操作设备修改。

地理位置信息如果获取失败（比如内网环境），则保留手动修改的信息，否则该信息会被替换为emqx取得到的地理信息。

#### send

```
{
    "device_id": str,
    "country": int,
    "country_name": str,
    "province": int,
    "province_name": str,
    "city": int,
    "city_name": str,
    "carrier": str,
    ["latitude": str,]
    ["longitude": str,]
    "remark": str
}
```

#### return

```
{
    "status": bool //是否成功
}
```
