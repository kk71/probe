NATS消息文档
===========

列出了python后端和node后端的nats消息名。

## nats消息收发主要思路

* 但凡源数据有变动，都触发一次数据发送，而不是差异化地发。

* 差异化地发部分数据需要更多额外代码来维护，发送整体的数据更加简单粗暴，并且更加可靠。

* 原本也有需要发送整体数据的需求。（比如python服务刚起来的时候需要拿到全部的组，任务信息等等）

* 特定数据（譬如数据量特别大的情况）可考虑分片发送或者差异化发送。

## 约定的nats操作后缀

以下约定仅对数据为主的请求作要求，如果是事务性的操作可随意。

* get请求获取全部数据

* post添加新数据

* put替换指定id的已有数据

* put_all替换全部数据

* delete删除指定id的数据

* updated数据源通知对方数据已更新

## 约定的nats主题结构

```
probe.[fe.][module name]..[postfix]
```

* ```[fe]```表示node发给python的请求，没有的表示python发给node的请求

* ```[postfix]```表示操作后缀

* ```[module name]```可用多个点连接

## 等待返回的NATS消息模式

指定NATS消息的reply即可

* 建议的reply格式：

```
<来源的消息subject>:<uuid>

e.g.
qaz.wsx.edc:08da1e54-bda8-4e23-ae1b-80f9a780822d
```