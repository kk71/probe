package com.yamu.bigdata.product.probe.sample.model;

import java.util.List;

public class ProbeResultTraceroute extends ProbeResult{

    // 配置的traceroute目标
    public String destination;

    // 实际traceroute的ip
    public String ip;

    // traceroute的路径
    public List<ProbeResultTracerouteRoute> routes;

}
