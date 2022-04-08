package com.yamu.bigdata.product.probe.sample.model;

import java.util.List;

/**
 * 拨测结果：http拨测
 */
public class ProbeResultHttpPageSpeedUp extends ProbeResult {

    // 拨测的url
    public String url;

    // url的域名，即"http://xxx:???"之中的xxx，不包括协议和端口号
    // 又称：hostname
    public String domain;

    // 使用的dns服务器
    public String dnsServer;

    // 各个ip的拨测结果
    public List<ProbeResultHttpIpResult> results;

}
