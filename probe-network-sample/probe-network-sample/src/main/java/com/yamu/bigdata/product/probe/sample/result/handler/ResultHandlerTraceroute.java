package com.yamu.bigdata.product.probe.sample.result.handler;

import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.sample.alert.ProbeAlertTraceroute;
import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.es.EsIp;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeData;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeDataPing;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeDataTraceroute;
import com.yamu.bigdata.product.probe.sample.utils.DtUtil;

import java.util.ArrayList;
import java.util.List;

public class ResultHandlerTraceroute extends ResultHandler {

    public ResultHandlerTraceroute(JSONObject originalJsonResult) {super(originalJsonResult);}

    @Override
    public ProbeResult packResult(JSONObject result) {
        ProbeResultTraceroute r = new ProbeResultTraceroute();

        r.createTime = DtUtil.localToUtc(result.getString("create_time"));
        r.probeTaskStatus = result.getString("probe_task_status");
        r.destination = result.getString("destination");
        r.ip = result.getString("ip");

        r.routes = new ArrayList<>();
        for (Object aRouteObject: result.getJSONArray("routes")) {
            JSONObject aRouteJson = (JSONObject) aRouteObject;
            ProbeResultTracerouteRoute aRoute = new ProbeResultTracerouteRoute();
            aRoute.ip = aRouteJson.getString("ip");
            aRoute.distance = aRouteJson.getInteger("distance");
            aRoute.minRtt = aRouteJson.getDouble("min_rtt");
            aRoute.maxRtt = aRouteJson.getDouble("max_rtt");
            aRoute.avgRtt = aRouteJson.getDouble("avg_rtt");
            aRoute.packetsSent = aRouteJson.getInteger("packets_sent");
            aRoute.packetsReceived = aRouteJson.getInteger("packets_received");
            aRoute.packetLoss = aRouteJson.getDouble("packet_loss");
            aRoute.avgRtt = aRouteJson.getDouble("avg_rtt");
            aRoute.location = new EsIp(aRoute.ip);
            r.routes.add(aRoute);
        }
        return r;
    }

    @Override
    public List<Target> packTargets(JSONObject task) {
        List<Target> r = new ArrayList<>();
        for (Object aTarget: task.getJSONArray("target")) {
            JSONObject target = (JSONObject) aTarget;
            TargetTraceroute targetTraceroute = new TargetTraceroute();
            targetTraceroute.data = target.getString("data");
            r.add(targetTraceroute);
        }
        return r;
    }

    @Override
    public ArrayList<EsProbeData> packEsTask() {
        ArrayList<EsProbeData> r = new ArrayList<>();
        for (ProbeResult probeResult: this.probeResults) {
            EsProbeDataTraceroute item = new EsProbeDataTraceroute(
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
        probeAlert = new ProbeAlertTraceroute();
        probeAlert.probeDataAlert(taskProbingId, task, this.probeDevice, clientId, results, true);
        return System.currentTimeMillis() - start;
    }

}
