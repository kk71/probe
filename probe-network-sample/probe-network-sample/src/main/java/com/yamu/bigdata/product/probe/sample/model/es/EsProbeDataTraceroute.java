package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.*;

import java.util.ArrayList;
import java.util.List;

public class EsProbeDataTraceroute extends EsProbeData {

    // traceroute的拨测目标
    public String destination;

    // 实际traceroute的ip
    public String ip;

    // traceroute的路径
    public List<EsProbeDataTracerouteRoute> routes;

    // 最后一跳
    public EsProbeDataTracerouteRoute last_route;

    // 最后一条的延时
    public String delay;

    public EsProbeDataTraceroute(
            String taskProbingId,
            ProbeTask probeTask,
            ProbeDevice probeDevice,
            ProbeResult probeResult) {
        super(taskProbingId, probeTask, probeDevice, probeResult);
    }

    public void putProbeResult(ProbeResult probeResult) {
        super.putProbeResult(probeResult);

        ProbeResultTraceroute r = (ProbeResultTraceroute) probeResult;
        this.destination = r.destination;
        this.ip = r.ip;
        this.routes = new ArrayList<EsProbeDataTracerouteRoute>();
        for (ProbeResultTracerouteRoute route: r.routes) {
            this.routes.add(new EsProbeDataTracerouteRoute(route));
        }
        if (this.routes.size()!=0) {
            this.last_route = this.routes.get(this.routes.size() - 1);
            this.delay = this.last_route.avg_rtt.toString();
        }
    }

}
