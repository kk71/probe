系统告警类型
==========

## 基本结构

```
{
    "type": str //告警类型限定符
    "description": str //告警描述
    "detail": str //代码层面的报错信息
    "create_time": "yyyy-mm-dd hh:mm:ss" //告警抛出本地时间文本
    "appendent": {...}  // 一些附加的信息结构
}
```

## nats 主题

probe.sys_notification

## sys_notification

未分类的系统警告

### sys_notification.service_unavailable

系统服务不可用

## sys_notification.probe

拨测端相关告警

### sys_notification.probe.low_online_rate

拨测设备在线率低于阈值

### sys_notification.probe.no_probe_within_region

某个区域内无任何可用拨测点

### sys_notification.probe.no_probe_for_task

某个拨测任务在某次拨测中找不到任何可用设备
