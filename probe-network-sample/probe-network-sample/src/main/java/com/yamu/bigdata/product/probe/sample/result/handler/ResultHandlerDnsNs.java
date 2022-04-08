package com.yamu.bigdata.product.probe.sample.result.handler;

import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.sample.alert.ProbeAlertDns;
import com.yamu.bigdata.product.probe.sample.alert.ProbeAlertDnsNs;
import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.es.EsIp;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeData;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeDataDns;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeDataDnsNs;
import com.yamu.bigdata.product.probe.sample.utils.DtUtil;

import java.util.ArrayList;
import java.util.List;

/**
 * dns-dnsNSHijack
 */
public class ResultHandlerDnsNs extends ResultHandlerDns {

    public ResultHandlerDnsNs(JSONObject originalJsonResult) {
        super(originalJsonResult);
    }

    @Override
    public ProbeResult packResult(JSONObject result) {
        ProbeResultDns pr = new ProbeResultDns();

        String dnsServerIp = result.getString("dns_server");
        EsIp esIp = new EsIp(dnsServerIp);
        pr.dns_server = esIp;
        pr.dns_response_status = result.getString("rcode");
        pr.rcode = result.getString("rcode");
        pr.probeTaskStatus = result.getString("probe_task_status");
        pr.jsonObject = result;
        pr.domain = result.getString("domain");
        pr.rrtype = result.getString("rdtype");
        pr.delay = result.getString("delay");
        pr.ttl = result.getString("ttl");
        pr.createTime = DtUtil.localToUtc(result.getString("create_time"));

        // 注意只有answer_section设置了results_a
        pr.answerSection = new ProbeResultDnsSectionListNs();
        pr.answerSection.setSections(result.getJSONArray("answer_section"));

        pr.authoritySection = new ProbeResultDnsSectionList();
        pr.authoritySection.setSections(result.getJSONArray("authority_section"));
        pr.additionalSection = new ProbeResultDnsSectionList();
        pr.additionalSection.setSections(result.getJSONArray("additional_section"));
        return pr;
    }

    @Override
    public ArrayList<EsProbeData> packEsTask() {
        ArrayList<EsProbeData> r = new ArrayList<>();
        for (ProbeResult probeResult: this.probeResults) {
            EsProbeDataDnsNs item = new EsProbeDataDnsNs(
                    this.taskProbingId, this.probeTask, this.probeDevice, probeResult);
            r.add(item);
        }
        return r;
    }

    @Override
    public Long alertRunInThread(
            String taskProbingId,
            ProbeTask task,
            String clientId,
            List<ProbeResult> results
    ) {
        long start = System.currentTimeMillis();
        probeAlert = new ProbeAlertDnsNs();
        probeAlert.probeDataAlert(taskProbingId, task, this.probeDevice, clientId, results, true);
        return System.currentTimeMillis() - start;
    }
}
