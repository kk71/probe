package com.yamu.bigdata.product.probe.sample.alert;

import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.nats.Alert;
import com.yamu.bigdata.product.probe.sample.model.nats.AlertPing;
import com.yamu.bigdata.product.probe.sample.model.nats.AlertPingLossRate;

import java.util.*;

public class ProbeAlertPing extends ProbeAlert {

    // ========================告警类型=============================
    // 响应超时
    public final String probePingResponseTimeout = "probePingResponseTimeout";
    // 延时（ping的delay）大于
    public final String probePingResponseLargeLatency = "probePingResponseLargeLatency";
    // 丢包率大于
    public final String probePingPacketLossRate = "probePingPacketLossRate";

    // 统计丢包率用的仓库
    protected static final ArrayList<PingLossRateCartridge> lossRateCartridges = new ArrayList();

    /**
     * 计算丢包率
     * @param clientId
     * @param destination
     * @param lossOrNot
     * @return
     */
    protected synchronized Double calculateLossRate(
            String clientId, String destination, Boolean lossOrNot) {
        PingLossRateCartridge currentCartridge = null;
        for (PingLossRateCartridge pingLossRateCartridge: lossRateCartridges) {
            if (pingLossRateCartridge.clientId.equals(clientId) &&
                    pingLossRateCartridge.destination.equals(destination)) {
                currentCartridge = pingLossRateCartridge;
            }
        }
        if (currentCartridge == null) {
            currentCartridge = new PingLossRateCartridge(clientId, destination);
            lossRateCartridges.add(currentCartridge);
        }
        currentCartridge.addSignature(lossOrNot);
        return currentCartridge.getLossRate();
    }

    protected AlertPing loadAlert(
            ProbeResultPing result,
            ProbeTask task,
            String clientId,
            String alertType) {
        AlertPing alert = new AlertPing();

        alert.alarmType = alertType;
        alert.alarmObject = clientId;
        alert.task_id = task.taskId;
        TargetPing targetPing = new TargetPing();
        targetPing.data = task.targets.get(0).data;
        alert.target = targetPing;

        alert.delay = result.delay;
        alert.alarmType = alertType;
        alert.probe_task_status = result.probeTaskStatus;
        alert.destination = result.destination;
        alert.ip = result.ip;
        alert.add_time = System.currentTimeMillis() + "";
        return alert;
    }

    protected AlertPing loadAlert(
            ProbeResultPing result,
            ProbeTask task,
            String clientId,
            String alertType,
            AlertPingLossRate lossRate) {
        AlertPing alert = this.loadAlert(result, task, clientId, alertType);
        alert.loss_rate = lossRate;
        return alert;
    }

    public List<Alert> probeDataAlert(
            String taskProbingId,
            ProbeTask task,
            ProbeDevice probeDevice,
            String clientId,
            List<ProbeResult> results,
            boolean isSendAlert) {
        List<Alert> alertList = new ArrayList<>();
        List<AlarmRule> rulesList = alertRuleUtil.getAlertRulesByTaskId(task.taskId);
        for (AlarmRule alarmRule : rulesList) {
            for (ProbeResult probeResult: results) {
                ProbeResultPing probeResultPing = (ProbeResultPing) probeResult;

                if (alarmRule.getAlert_type().equals(this.probePingResponseTimeout)) {
                    if (probeResultPing.probeTaskStatus.equals(ProbeResult.probeTaskStatusTimeout) ||
                        probeResultPing.probeTaskStatus.equals(ProbeResult.probeTaskStatusDnsResolveFailed)) {
                        alertList.add(loadAlert(
                                probeResultPing, task, clientId, probePingResponseTimeout));
                    }

                } else if (alarmRule.getAlert_type().equals(this.probePingResponseLargeLatency)) {
                    if (AlarmRule.opGt.equals(alarmRule.getOp())) {
                        if (probeResultPing.delay != null &&
                                probeResultPing.delay > Double.parseDouble(alarmRule.getValue()[0])) {
                            alertList.add(loadAlert(
                                    probeResultPing, task, clientId, probePingResponseLargeLatency));
                        }
                    }

                } else if (alarmRule.getAlert_type().equals(this.probePingPacketLossRate)) {
                    if (AlarmRule.opGt.equals(alarmRule.getOp())) {
                        Boolean lossOrNot = false;
                        if (probeResultPing.delay == null) {
                            lossOrNot = true;
                        }
                        Double currentPacketLossRate = this.calculateLossRate(
                                clientId, probeResultPing.destination, lossOrNot);
                        if (currentPacketLossRate > Double.parseDouble(alarmRule.getValue()[0])) {
                            AlertPingLossRate alertPingLossRate = new AlertPingLossRate();
                            alertPingLossRate.loss_rate = currentPacketLossRate;
                            alertPingLossRate.client_id = clientId;
                            alertList.add(loadAlert(
                                    probeResultPing, task, clientId, probePingPacketLossRate, alertPingLossRate));
                        }
                    }

                }
            }
        }

        // 判断是否发送告警
        if (isSendAlert && alertList.size() >= 1) {
            probeAlert(alertList);
        }

        return alertList;

    }

}
