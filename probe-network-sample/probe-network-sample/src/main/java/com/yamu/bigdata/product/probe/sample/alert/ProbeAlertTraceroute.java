package com.yamu.bigdata.product.probe.sample.alert;

import com.yamu.bigdata.product.probe.sample.model.ProbeDevice;
import com.yamu.bigdata.product.probe.sample.model.nats.Alert;
import com.yamu.bigdata.product.probe.sample.model.ProbeResult;
import com.yamu.bigdata.product.probe.sample.model.ProbeTask;

import java.util.ArrayList;
import java.util.List;

public class ProbeAlertTraceroute extends ProbeAlert {

    public List<Alert> probeDataAlert(
            String taskProbingId,
            ProbeTask task,
            ProbeDevice probeDevice,
            String clientId,
            List<ProbeResult> results,
            boolean isSendAlert) {
        List<Alert> alertList = new ArrayList<>();
        return alertList;
    }
}
