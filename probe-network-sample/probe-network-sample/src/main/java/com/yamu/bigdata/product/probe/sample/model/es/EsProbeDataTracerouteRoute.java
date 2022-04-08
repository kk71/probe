package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.GeoPoint;
import com.yamu.bigdata.product.probe.sample.model.ProbeResultTracerouteRoute;

public class EsProbeDataTracerouteRoute {

    // ip
    public String ip;

    // 距离
    public Integer distance;

    // 发出的包数
    public Integer packets_sent;

    // 收到的包数
    public Integer packets_received;

    // 丢包率
    public Double packet_loss;

    public Double min_rtt;

    public Double max_rtt;

    public Double avg_rtt;

    // 当前跳的地理运营商信息
    public EsIp location;


    public EsProbeDataTracerouteRoute(ProbeResultTracerouteRoute route) {
        this.ip = route.ip;
        this.distance = route.distance;
        this.packets_sent = route.packetsSent;
        this.packets_received = route.packetsReceived;
        this.packet_loss = route.packetLoss;
        this.min_rtt = route.minRtt;
        this.max_rtt = route.maxRtt;
        this.avg_rtt = route.avgRtt;
        this.location = route.location;
    }

}
