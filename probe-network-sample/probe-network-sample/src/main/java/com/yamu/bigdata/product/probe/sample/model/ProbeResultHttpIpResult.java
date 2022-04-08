package com.yamu.bigdata.product.probe.sample.model;

import com.alibaba.fastjson.JSONObject;

/**
 * mqtt的http类型拨测的ip对应result
 */
public class ProbeResultHttpIpResult {

    // ip
    public String ip;

    // 响应时间
    public Double responseTime;

    // 当前的ip的拨测结果
    public String probeTaskStatus;


    public ProbeResultHttpIpResult(JSONObject originalJson) {
        this.ip = originalJson.getString("ip");
        this.responseTime = Double.parseDouble(originalJson.getString("response_time"));
        this.probeTaskStatus = originalJson.getString("probe_task_status");
    }

}
