package com.yamu.bigdata.product.probe.sample.model.es;

/**
 * http拨测中的http信息字段
 */
public class EsTaskRecordHttpInfo {

    // 拨测的url
    public String url;

    // url的域名，即"http://xxx:???"之中的xxx，不包括协议和端口号
    // 又称：hostname
    public String domain;

    // 使用的dns服务器
    public String dns_server;

    // 根据上述dns服务器解析到的ip
    public String ip;

    // 响应时间
    public Double response_time;

    // 拨测时间utc
    public String create_time;

    // 本次http请求的拨测状态
    // 请注意：本数据结构处在EsTaskRecord内，
    // EsTaskRecord还有一个probe_task_status,那个是专门指dns域名解析的状态
    // 因为http请求通常是域名，那么域名解析是后续请求的基础
    public String probe_task_status;

}
