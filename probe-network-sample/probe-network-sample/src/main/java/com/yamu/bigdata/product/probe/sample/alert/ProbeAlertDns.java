package com.yamu.bigdata.product.probe.sample.alert;

import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.nats.Alert;
import com.yamu.bigdata.product.probe.sample.model.nats.AlertDns;
import com.yamu.bigdata.product.probe.sample.model.nats.AlertDnsResolveSuccessRate;
import com.yamu.bigdata.product.probe.sample.utils.RedisConnectorOutNet;

import java.util.*;

/**
 * 拨测告警：dns
 */
public class ProbeAlertDns extends ProbeAlert {

    // ========================告警类型=============================
    // NS记录告警
    public final String probeDnsNSHijackAlarm = "probeDnsNSHijackAlarm";
    // NS CNAME的A记录告警
    public final String probeDnsNSAHijackAlarm = "probeDnsNSAHijackAlarm";

    /**
     * 与大数据对接的特殊告警：根据接口获得的IP，判断DNS解析结果的IP是否在范围内，
     * 如果不在，则触发出网告警。
     * 这个告警规则不需要用户手动在页面上配置，任务通过接口调用ems的后端，
     * ems后端会在创建任务的时候自动加入此告警规则
     */
    public final String probeDnsOutOfNetAlarm = "probeDnsOutOfNetAlarm";

    /**
     * 出网所需要的redis
     */
    protected RedisConnectorOutNet redisConnectorOutNet;

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
        List<Alert> alertList = new ArrayList<>();

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

            /**
             * 特殊规则：域名列表拨测成功率
             * 该规则是需要遍历全部拨测数据的，单独处理
             */
            if ("resolve_success_rate".equals(ruleField)) {
                List<ProbeResultDns> probeResultDnsList = new ArrayList<>();
                for (ProbeResult probeResult: results) {
                    probeResultDnsList.add((ProbeResultDns) probeResult);
                }
                AlertDnsResolveSuccessRate a = this.parseResolveSuccessRate(
                        taskProbingId,
                        probeResultDnsList,
                        task,
                        clientId,
                        ruleAlertType
                );
                Float successRate = Float.parseFloat(
                        a.succeess_rate.replace("%", ""));
                assert ruleOnlyOneValue != null;
                if (successRate < Float.parseFloat(ruleOnlyOneValue)) {
                    alertList.add(a);
                }
            }

            for (ProbeResult probeResult: results) {

                ProbeResultDns probeResultDns = (ProbeResultDns)  probeResult;
                // 全A的解析结果列表
                ArrayList<String> answer = probeResultDns.answerSection.getSectionsWithRdtype(probeResultDns.rrtype);

                if (rule.getAlert_type().equals(this.probeDnsOutOfNetAlarm)) {
                    /**
                     * 处理给大数据开发的特殊dns解析结果告警
                     */
                    loadAlertOutOfNet(alertList, probeResultDns, probeDevice, task, clientId);
                }

                if ("answer".equals(ruleField)) {

                    //解析结果集为空告警
                    if (AlarmRule.opEmpty.equals(ruleOp) &&
                            probeResultDns.answerSection.getSections().size() == 0) {
                        alertList.add(loadAlert(
                                probeResultDns, task.taskId, clientId, ruleAlertType));
                        continue;
                    }

                    for (String answerIp: answer) {

                        // in 在结果集
                        if (AlarmRule.opIn.equals(ruleOp) && ruleValueList.contains(answerIp)) {
                            alertList.add(loadAlert(
                                    probeResultDns, task.taskId, clientId, ruleAlertType));
                            continue;
                        }

                        // notIn 不在结果集
                        if (AlarmRule.opNotIn.equals(ruleOp) && !ruleValueList.contains(answerIp)) {
                            alertList.add(loadAlert(
                                    probeResultDns, task.taskId, clientId, ruleAlertType));
                        }
                    }

                } else {
                    String resultRuleFieldValue = probeResultDns.jsonObject.getString(ruleField);

                    // in 在结果集
                    if (AlarmRule.opIn.equals(ruleOp) && ruleValueList.contains(resultRuleFieldValue)) {
                        alertList.add(loadAlert(
                                probeResultDns, task.taskId, clientId, ruleAlertType));
                        continue;
                    }

                    // notIn 不在结果集
                    if (AlarmRule.opNotIn.equals(ruleOp) && !ruleValueList.contains(resultRuleFieldValue)) {
                        alertList.add(loadAlert(
                                probeResultDns, task.taskId, clientId, ruleAlertType));
                        continue;
                    }

                    // eq 返回码状态等于,
                    if (AlarmRule.opEq.equals(ruleOp) && ruleOnlyOneValue.equals(resultRuleFieldValue)) {
                        alertList.add(loadAlert(
                                probeResultDns, task.taskId, clientId, ruleAlertType));
                        continue;
                    }

                    //eq 解析结果等于 answer_set
                    if (AlarmRule.opEq.equals(ruleOp)) {
                        if (answer.size() == 1 && answer.get(0).equals(ruleOnlyOneValue)) {
                            alertList.add(loadAlert(
                                    probeResultDns, task.taskId, clientId, ruleAlertType));
                            continue;
                        }
                    }
                    //empty
                    if (AlarmRule.opEmpty.equals(ruleOp) && answer.size() == 0) {
                        alertList.add(loadAlert(
                                probeResultDns, task.taskId, clientId, ruleAlertType));
                        continue;
                    }

                    // ne 不等于
                    if (AlarmRule.opNe.equals(ruleOp)) {
                        assert ruleOnlyOneValue != null;
                        if (!ruleOnlyOneValue.equals(resultRuleFieldValue)) {
                            alertList.add(loadAlert(
                                    probeResultDns, task.taskId, clientId, ruleAlertType));
                            continue;
                        }
                    }

                    // gt 大于
                    if (AlarmRule.opGt.equals(ruleOp)) {
                        // 判断是否为数组
                        assert ruleValue != null;
                        if (ruleValue.length > 1) {
                            for (String value : ruleValue) {
                                if (Double.parseDouble(resultRuleFieldValue) > Double.parseDouble(value)) {
                                    alertList.add(loadAlert(
                                            probeResultDns, task.taskId, clientId, ruleAlertType));
                                }
                            }
                        } else if (ruleValue.length == 1) {
                            if ((resultRuleFieldValue != null) && (Double.parseDouble(resultRuleFieldValue) > Double.parseDouble(ruleOnlyOneValue))) {
                                alertList.add(loadAlert(
                                        probeResultDns, task.taskId, clientId, ruleAlertType));
                            }
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

    /**
     * 处理发送域名列表的解析成功率告警
     * @param taskProbingId
     * @param results
     * @param task
     * @param clientId
     * @param alertType
     * @return
     */
    private AlertDnsResolveSuccessRate parseResolveSuccessRate(
            String taskProbingId,
            List<ProbeResultDns> results,
            ProbeTask task,
            String clientId,
            String alertType) {

        AlertDnsResolveSuccessRate alert = new AlertDnsResolveSuccessRate();
        alert.uuid = taskProbingId;
        alert.domain_group_length = results.size();
        alert.task_id = task.taskId;
        alert.alarmObject = clientId;
        alert.alarmType = alertType;
        alert.add_time = System.currentTimeMillis() + "";
        alert.target = task.targets.get(0);
        alert.total_probe_count = 0;
        alert.success_probe_count = 0;

        for (ProbeResultDns probeResultDns: results) {
            alert.total_probe_count += 1;
            if (probeResultDns.probeTaskStatus.equals(ProbeResult.probeTaskStatusSuccessful)
                    && probeResultDns.answerSection != null
                    && probeResultDns.answerSection.getSectionsWithRdtype(probeResultDns.rrtype).size() != 0) {
                alert.success_probe_count += 1;
            }
        }
        alert.calculateSuccessRate();
        return alert;

    }

    /**
     * 装载告警对象
     */
    public AlertDns loadAlert(
            ProbeResultDns result,
            String taskId,
            String clientId,
            String alertType) {
        AlertDns alert = new AlertDns();

        alert.task_id = taskId;
        alert.alarmObject = clientId;
        alert.alarmType = alertType;
        alert.server = result.dns_server.getIp();

        alert.add_time = System.currentTimeMillis() + "";
        TargetDns target = new TargetDns();
        target.rrtype = result.rrtype;
        target.data = result.domain;
        alert.answer = result.answerSection.getSectionsWithRdtype(result.rrtype).toArray(new String[0]);
        alert.target = target;
        String delay = result.delay;
        if (delay != null) {
            alert.delay = Float.parseFloat(delay);
        }
        alert.probe_task_status = result.probeTaskStatus;
        alert.status = result.rcode;
        return alert;
    }

    /**
     * 给大数据专门写的出网告警。
     * 即：当前给定的dns解析结果不在指定的范围内
     * 具体：当前给定的A记录解析结果所在的区域，不在大数据指定的IP集合内。
     * 该集合是从接口获取的数据，存入redis，每个星期更新一次
     */
    private void loadAlertOutOfNet(
            List<Alert> alertList,
            ProbeResultDns probeResultDns,
            ProbeDevice probeDevice,
            ProbeTask task,
            String clientId) {
        if (this.redisConnectorOutNet==null) {
            this.redisConnectorOutNet = new RedisConnectorOutNet();
        }
        String province = probeDevice.getClient_ip().getProvince();
        String city = probeDevice.getClient_ip().getCity();
        String carrier = probeDevice.getClient_ip().getCarrier();
        ArrayList<String> aRecordsList = probeResultDns.answerSection.getSectionsWithRdtype("A");
        ArrayList<String> ips = this.redisConnectorOutNet.query();
        for (String aRecord: aRecordsList) {
            if (ips.size()==0||!ips.contains(aRecord)) {
                // 增加：ips的长度为0，即接口没有任何数据的情况下，也告警
                alertList.add(loadAlert(
                        probeResultDns, task.taskId, clientId, probeDnsOutOfNetAlarm));
            }
        }
    }

}
