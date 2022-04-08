package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.ProbeDevice;
import com.yamu.bigdata.product.probe.sample.model.ProbeResult;
import com.yamu.bigdata.product.probe.sample.model.ProbeResultDns;
import com.yamu.bigdata.product.probe.sample.model.ProbeTask;

import java.util.ArrayList;
import java.util.List;


/**
 * es拨测结果数据: dns拨测
 */
public class EsProbeDataDns extends EsProbeData {

    public EsProbeDataDns(
            String taskProbingId,
            ProbeTask probeTask,
            ProbeDevice probeDevice,
            ProbeResult probeResult) {
        super(taskProbingId, probeTask, probeDevice, probeResult);
    }

    // dns拨测的类型（A CNAME NS ..）
    public String rrtype;

    // 延时
    public String delay;

    // ttl
    public String ttl;

    // 目标域名
    public String domain;

    // 应答ip
    public List<EsProbeDataDnsAnswer> answer;

    // dns响应状态
    public String dns_response_status;

    /**
     * 创建结果信息
     * @param probeResult
     * @return
     */
    public void putProbeResult(ProbeResult probeResult) {
        super.putProbeResult(probeResult);

        ProbeResultDns probeResultDns = (ProbeResultDns) probeResult;
        this.rrtype = probeResultDns.rrtype;
        this.dns_server_ip = probeResultDns.dns_server;
        this.delay = probeResultDns.delay;
        this.ttl = probeResultDns.ttl;
        this.domain = probeResultDns.domain;
        this.dns_response_status = probeResultDns.dns_response_status;
        this.end_time = probeResultDns.createTime;
        putAnswer(probeResultDns);
    }

    /**
     * 增加answer
     * @param probeResultDns
     */
    protected void putAnswer(ProbeResultDns probeResultDns) {
        this.answer = new ArrayList<>();
        for (String ip: probeResultDns.answerSection.getSectionsWithRdtype(probeResultDns.rrtype)) {
            this.answer.add(new EsProbeDataDnsAnswer(ip));
        }
    }

}
