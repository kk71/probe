package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.*;

/**
 * http页面提速优化拨测
 */
public class EsProbeDataHttpPageSpeedUp extends EsProbeData {

    // http请求的结果
    // 请注意：【域名-dns服务器-解析到的IP】为单位记录一次http拨测，
    // 在mqtt传来的数据中，【域名-dns服务器】作为以一个单一的拨测结果，解析到的IP不同，放在列表里
    public EsTaskRecordHttpInfo http_info;

    /**
     * @param taskProbingId
     * @param probeTask
     * @param probeDevice
     * @param probeResult
     * @param resultIndex 使用results中的哪一个作为es的拨测记录
     */
    public EsProbeDataHttpPageSpeedUp(
            String taskProbingId,
            ProbeTask probeTask,
            ProbeDevice probeDevice,
            ProbeResult probeResult,
            Integer resultIndex) {
        this.putProbeDevice(probeDevice);
        this.putTask(taskProbingId, probeTask);
        this.putProbeResult(probeResult, resultIndex);
    }

    /**
     * mqtt传来的results是个列表，封装到es结构中需要拆解
     * @param probeResult
     * @param resultsIndex 使用原results列表中的哪个拨测结果
     */
    public void putProbeResult(ProbeResult probeResult, Integer resultsIndex) {
        super.putProbeResult(probeResult);
        ProbeResultHttpPageSpeedUp probeResultHttpPageSpeedUp = (ProbeResultHttpPageSpeedUp) probeResult;
        this.http_info = new EsTaskRecordHttpInfo();
        this.http_info.url = probeResultHttpPageSpeedUp.url;
        this.http_info.dns_server = probeResultHttpPageSpeedUp.dnsServer;
        this.http_info.domain = probeResultHttpPageSpeedUp.domain;
        this.http_info.ip = probeResultHttpPageSpeedUp.results.get(resultsIndex).ip;
        this.http_info.response_time = probeResultHttpPageSpeedUp.results.get(resultsIndex).responseTime;
        this.http_info.create_time = probeResultHttpPageSpeedUp.createTime;
        this.http_info.probe_task_status = probeResultHttpPageSpeedUp.results.get(resultsIndex).probeTaskStatus;
    }
}
