package com.yamu.bigdata.product.probe.sample.model.nats;

/**
 * 丢包率相关的告警信息
 */
public class AlertPingLossRate {

    // 丢包率相关的拨测端client_id
    public String client_id;

    // 丢包率
    public Double loss_rate;

}
