package com.yamu.bigdata.product.probe.sample.model.nats;

/**
 * 告警数据结构：ping
 */
public class AlertPing extends Alert {

    // 拨测目标
    public String destination;

    // ip
    public String ip;

    // 延迟
    public Double delay;

    // 丢包率
    public AlertPingLossRate loss_rate;

}
