package com.yamu.bigdata.product.probe.sample.model;

import com.yamu.bigdata.product.probe.sample.model.es.EsIp;

/**
 * dns的拨测结果
 */
public class ProbeResultDns extends ProbeResult {

    //
    public String rrtype;

    // 延时
    public String delay;

    // ttl
    public String ttl;

    // 目标域名
    public String domain;

    // answer
    public ProbeResultDnsSectionList answerSection;

    // authority
    public ProbeResultDnsSectionList authoritySection;

    // additional
    public ProbeResultDnsSectionList additionalSection;

    // dns响应状态
    public String rcode;
    @Deprecated
    public String dns_response_status; // TODO 等同于rcode

}
