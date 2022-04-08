package com.yamu.bigdata.product.probe.sample.result.handler;

import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.sample.alert.ProbeAlertDns;
import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.es.EsIp;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeData;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeDataDns;
import com.yamu.bigdata.product.probe.sample.utils.DtUtil;
import com.yamu.bigdata.product.probe.sample.utils.RedisConnectorTaskProbingId;

import java.util.ArrayList;
import java.util.List;

public class ResultHandlerDns extends ResultHandler {

    public ResultHandlerDns(JSONObject originalJsonResult) {
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
        pr.answerSection = new ProbeResultDnsSectionList();
        pr.answerSection.setSections(result.getJSONArray("answer_section"));
        pr.authoritySection = new ProbeResultDnsSectionList();
        pr.authoritySection.setSections(result.getJSONArray("authority_section"));
        pr.additionalSection = new ProbeResultDnsSectionList();
        pr.additionalSection.setSections(result.getJSONArray("additional_section"));
        return pr;
    }

    @Override
    public List<Target> packTargets(JSONObject task) {
        List<Target> r = new ArrayList<>();
        for (Object aTarget: task.getJSONArray("target")) {
            JSONObject target = (JSONObject) aTarget;
            TargetDns targetDns = new TargetDns();
            targetDns.rrtype = target.getString("rrtype");
            targetDns.data = target.getString("data");
            r.add(targetDns);
        }
        return r;
    }

    @Override
    public ArrayList<EsProbeData> packEsTask() {
        ArrayList<EsProbeData> r = new ArrayList<>();
        for (ProbeResult probeResult: this.probeResults) {
            EsProbeDataDns item = new EsProbeDataDns(
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
        probeAlert = new ProbeAlertDns();
        probeAlert.probeDataAlert(taskProbingId, task, this.probeDevice, clientId, results, true);
        return System.currentTimeMillis() - start;
    }

    @Override
    protected void taskIsDone() {
        RedisConnectorTaskProbingId redisConnector = new RedisConnectorTaskProbingId();
        redisConnector.insertNewTaskProbingId(this.probeTask.taskId, this.taskProbingId);
    }

}
