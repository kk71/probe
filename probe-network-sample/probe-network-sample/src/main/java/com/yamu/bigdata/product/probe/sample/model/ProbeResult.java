package com.yamu.bigdata.product.probe.sample.model;

import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.sample.model.es.EsIp;

/**
 * emqx传来的拨测结果中的每一条拨测结果数据
 */
public class ProbeResult {

    // probe_task_status 的常量
    // 拨测成功
    public final static String probeTaskStatusSuccessful = "0";
    // 笼统的拨测失败
    public final static String probeTaskStatusFailed = "-1";
    // 拨测超时
    public final static String probeTaskStatusTimeout = "-2";
    // 非dns拨测的过程中，如果中间步骤涉及dns解析，然后解析失败了，则报此错
    @Deprecated
    public final static String probeTaskStatusDnsResolveFailed = "-3";

    // 拨测任务完成时间
    public String createTime;

    // new：拨测状态
    public String probeTaskStatus;

    // dns服务器ip
    public EsIp dns_server;

    // 保存json数据结构，用于规则查
    // 规则中记录字段名取值作大小比较
    public JSONObject jsonObject;

}
