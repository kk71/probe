package com.yamu.bigdata.product.probe.sample.result.handler;

import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.alert.*;
import com.yamu.bigdata.product.probe.sample.model.es.EsIp;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeData;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeDataPing;
import com.yamu.bigdata.product.probe.sample.utils.DtUtil;

import java.util.ArrayList;
import java.util.List;

public class ResultHandlerPing extends ResultHandler {

    public ResultHandlerPing(JSONObject originalJsonResult) {super(originalJsonResult);}

    @Override
    public ProbeResult packResult(JSONObject result) {
        ProbeResultPing r = new ProbeResultPing();

        r.createTime = DtUtil.localToUtc(result.getString("create_time"));
        r.probeTaskStatus = result.getString("probe_task_status");
        r.destination = result.getString("destination");
        r.ip = result.getString("ip");
        r.delay = result.getDouble("delay");

        // add dns server info
        String dnsServerIp = result.getString("dns_server");
        if (dnsServerIp!=null) {
            EsIp esIp = new EsIp(dnsServerIp);
            r.dns_server = esIp;
        }

        return r;
    }

    @Override
    public List<Target> packTargets(JSONObject task) {
        List<Target> r = new ArrayList<>();
        for (Object aTarget: task.getJSONArray("target")) {
            JSONObject target = (JSONObject) aTarget;
            TargetPing targetPing = new TargetPing();
            targetPing.data = target.getString("data");
            r.add(targetPing);
        }
        return r;
    }

    @Override
    public ArrayList<EsProbeData> packEsTask() {
        ArrayList<EsProbeData> r = new ArrayList<>();
        for (ProbeResult probeResult: this.probeResults) {
            EsProbeDataPing item = new EsProbeDataPing(
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
        probeAlert = new ProbeAlertPing();
        probeAlert.probeDataAlert(taskProbingId, task, this.probeDevice, clientId, results, true);
        return System.currentTimeMillis() - start;
    }

}
