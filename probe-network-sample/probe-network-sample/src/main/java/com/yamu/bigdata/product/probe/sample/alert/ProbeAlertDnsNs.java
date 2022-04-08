package com.yamu.bigdata.product.probe.sample.alert;

import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.nats.Alert;
import com.yamu.bigdata.product.probe.sample.model.nats.AlertDns;
import com.yamu.bigdata.product.probe.sample.model.nats.AlertDnsNs;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * dns-dnsNSHijack的告警
 */
public class ProbeAlertDnsNs extends ProbeAlertDns {

    public List<Alert> probeDataAlert(
            String taskProbingId,
            ProbeTask task,
            ProbeDevice probeDevice,
            String clientId,
            List<ProbeResult> results,
            boolean isSendAlert) {

        // 取规则
        List<AlarmRule> rulesList = alertRuleUtil.getAlertRulesByTaskId(task.taskId);
        // 告警对象列表
        List<Alert> alertList = super.probeDataAlert(taskProbingId, task, probeDevice, clientId, results, false);

        // 因为父类的方法里是不能判断probeDnsNSAHijackAlarm告警的，
        // 因此循环一下，如果发现告警了则删除
        List<Alert> clearedAlertList = new ArrayList<>();
        for (Alert alert: alertList) {
            if (!alert.alarmType.equals(this.probeDnsNSAHijackAlarm)) {
                clearedAlertList.add(alert);
            }
        }
        alertList = clearedAlertList;

        for (AlarmRule rule : rulesList) {

            String ruleField = rule.getField().toLowerCase();
            String ruleOp = rule.getOp().toLowerCase();
            String[] ruleValue = rule.getValue();
            List<String> ruleValueList;
            String ruleOnlyOneValue = null;
            if (ruleValue == null) {
                ruleValueList = new ArrayList<>();
            } else {
                ruleValueList = Arrays.asList(ruleValue);
                ruleOnlyOneValue = ruleValue[0].trim();
            }
            String ruleAlertType = rule.getAlert_type();

            for (ProbeResult probeResult : results) {

                ProbeResultDns probeResultDns = (ProbeResultDns) probeResult;

                // ==================
                // 此处仅补充NS告警需要的
                // NS的CNAME告警已经在外层处理掉了，这里只需要处理CNAME的A记录告警
                // ==================

                if (ruleAlertType.equals(this.probeDnsNSAHijackAlarm)) {
                    ArrayList<String> nsCnameARecords = new ArrayList<>();
                    for (ProbeResultDnsSection probeResultDnsSection: probeResultDns.answerSection.getSections()) {
                        ProbeResultDnsSectionNs probeResultDnsSectionNs = (ProbeResultDnsSectionNs) probeResultDnsSection;
                        for (ProbeResultDns innerProbeResultDns: probeResultDnsSectionNs.resultsA) {
                            for (String aRecord: innerProbeResultDns.answerSection.getSectionsWithRdtype("A")) {
                                nsCnameARecords.add(aRecord);
                            }
                        }
                    }
                    if (!ruleValueList.contains(nsCnameARecords)) {
//                        logger.info("rule" + ruleValueList + " , response: " + nsCnameARecords);
                        alertList.add(loadAlert(
                                probeResultDns, task.taskId, clientId, ruleAlertType, nsCnameARecords));
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

    /**
     * 装载告警对象
     * @param result
     * @param taskId
     * @param clientId
     * @param alertType
     * @param resultsA 实际拨测得到的NS记录的A记录值
     * @return
     */
    public AlertDns loadAlert(
            ProbeResultDns result,
            String taskId,
            String clientId,
            String alertType,
            ArrayList<String> resultsA) {
        AlertDnsNs alert = new AlertDnsNs();

        alert.task_id = taskId;
        alert.alarmObject = clientId;
        alert.alarmType = alertType;
        alert.server = result.dns_server.getIp();

        alert.add_time = System.currentTimeMillis() + "";
        TargetDns target = new TargetDns();
        target.rrtype = result.rrtype;
        target.data = result.domain;
        alert.answer = result.answerSection.getSectionsWithRdtype(result.rrtype).toArray(new String[0]);
        alert.answer_results_a = resultsA.toArray(new String[0]);
        alert.target = target;
        String delay = result.delay;
        if (delay != null) {
            alert.delay = Float.parseFloat(delay);
        }
        alert.probe_task_status = result.probeTaskStatus;
        alert.status = result.rcode;
        return alert;
    }
}
