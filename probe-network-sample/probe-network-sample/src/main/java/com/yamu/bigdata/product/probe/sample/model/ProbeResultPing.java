package com.yamu.bigdata.product.probe.sample.model;

import java.util.ArrayList;

/**
 * ping拨测的results内的结构
 */
public class ProbeResultPing extends ProbeResult {

    // 配置的ping目标
    public String destination;

    // 实际ping的ip
    public String ip;

    // 延迟秒
    public Double delay;

}
