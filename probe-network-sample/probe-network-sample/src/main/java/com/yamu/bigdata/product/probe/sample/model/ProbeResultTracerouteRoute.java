package com.yamu.bigdata.product.probe.sample.model;

import com.yamu.bigdata.product.probe.sample.model.es.EsIp;

/**
 * traceroute拨测的每一步
 */
public class ProbeResultTracerouteRoute {

    // ip
    public String ip;

    // 距离
    public Integer distance;

    // 发出的包数
    public Integer packetsSent;

    // 收到的包数
    public Integer packetsReceived;

    // 丢包率
    public Double packetLoss;

    public Double minRtt;

    public Double maxRtt;

    public Double avgRtt;

    public EsIp location;

}
