package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.ProbeDevice;
import com.yamu.bigdata.product.probe.sample.model.ProbeResult;
import com.yamu.bigdata.product.probe.sample.model.ProbeResultPing;
import com.yamu.bigdata.product.probe.sample.model.ProbeTask;


/**
 * es拨测结果数据: ping拨测
 */
public class EsProbeDataPing extends EsProbeData {

    // ping的拨测目标
    public String destination;

    // 实际ping的ip
    public String ip;

    // 延迟秒
    public Double delay;

    public EsProbeDataPing(
            String taskProbingId,
            ProbeTask probeTask,
            ProbeDevice probeDevice,
            ProbeResult probeResult) {
        super(taskProbingId, probeTask, probeDevice, probeResult);
    }

    public void putProbeResult(ProbeResult probeResult) {
        super.putProbeResult(probeResult);

        ProbeResultPing probeResultPing = (ProbeResultPing) probeResult;
        this.destination = probeResultPing.destination;
        this.ip = probeResultPing.ip;
        this.delay = probeResultPing.delay;
        this.dns_server_ip = probeResultPing.dns_server;
    }

}
