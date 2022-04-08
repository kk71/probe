package com.yamu.bigdata.product.probe.sample.model.nats;

/**
 * 告警数据结构：dns
 */
public class AlertDns extends Alert {

    // dns服务器ip
    public String server;

    // dns响应
    public String[] answer;

    // 延时
    public float delay;

    // dns拨测rcode
    public String status;

}
