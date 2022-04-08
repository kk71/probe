package com.yamu.bigdata.product.probe.sample.result.handler;

import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.sample.alert.ProbeAlertPing;
import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeData;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeDataHttpPageSpeedUp;
import com.yamu.bigdata.product.probe.sample.utils.RedisConnectorTaskProbingId;

import java.util.ArrayList;
import java.util.List;

/**
 * http拨测
 */
public class ResultHandlerHttpPageSpeedUp extends ResultHandler {

    public ResultHandlerHttpPageSpeedUp(JSONObject originalJsonResult) {super(originalJsonResult);}

    @Override
    public ProbeResult packResult(JSONObject result) {
        ProbeResultHttpPageSpeedUp r = new ProbeResultHttpPageSpeedUp();
        r.url = result.getString("url");
        r.domain = result.getString("domain");
        r.dnsServer = result.getString("dns_server");
        r.results = new ArrayList<>();
        for (Object ipResult: result.getJSONArray("results")) {
            JSONObject ipResultJsonObject = (JSONObject) ipResult;
            r.results.add(new ProbeResultHttpIpResult(ipResultJsonObject));
        }
        r.probeTaskStatus = result.getString("probe_task_status");
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
        for (ProbeResult rr: this.probeResults) {
            ProbeResultHttpPageSpeedUp probeResultHttpPageSpeedUp = (ProbeResultHttpPageSpeedUp) rr;
            for (Integer i = 0; i < probeResultHttpPageSpeedUp.results.size(); i++) {
                EsProbeDataHttpPageSpeedUp item = new EsProbeDataHttpPageSpeedUp(
                        taskProbingId, probeTask, probeDevice, probeResultHttpPageSpeedUp, i);
                r.add(item);
            }
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

    @Override
    protected void taskIsDone() {
        RedisConnectorTaskProbingId redisConnector = new RedisConnectorTaskProbingId();
        redisConnector.insertNewTaskProbingId(this.probeTask.taskId, this.taskProbingId);
    }
}
