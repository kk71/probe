package com.yamu.bigdata.product.probe.sample.alert;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.serializer.SerializerFeature;
import com.yamu.bigdata.product.probe.sample.model.ProbeDevice;
import com.yamu.bigdata.product.probe.sample.model.nats.Alert;
import com.yamu.bigdata.product.probe.sample.model.ProbeResult;
import com.yamu.bigdata.product.probe.sample.model.ProbeTask;
import com.yamu.bigdata.product.probe.sample.utils.AlertRuleUtil;
import com.yamu.bigdata.product.probe.sample.utils.NatsUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

/**
 * 拨测结果告警
 * 告警规则:
 * 不在结果集
 * 域名劫持告警:probeDnsHijackAlarm
 * 解析延时
 * 延时过高告警:probeDnsResolveLargeLatency
 * 延时超时告警:probeDnsResolveTimeout
 * 返回码
 * 无效返回码告警:probeDnsResolveInvalidRCode
 * @author wedo
 */
public abstract class ProbeAlert {

    protected Logger logger = LoggerFactory.getLogger(ProbeAlert.class);
    static NatsUtil natsUtil = new NatsUtil();
    protected AlertRuleUtil alertRuleUtil = new AlertRuleUtil();

    /**
     * 分析、生成告警
     * 传入封装好的list of results
     * @param taskProbingId
     * @param task
     * @param clientId
     * @param results
     * @param isSendAlert
     * @return
     */
    public abstract List<Alert> probeDataAlert(
            String taskProbingId,
            ProbeTask task,
            ProbeDevice probeDevice,
            String clientId,
            List<ProbeResult> results,
            boolean isSendAlert);

    /**
     * 发送告警
     */
    public void probeAlert(List<Alert> alerts) {
        for (Alert alert : alerts) {
            String alertString = JSON.toJSONString(alert, SerializerFeature.WriteMapNullValue);
            logger.info("pushing alert: " + alertString);
            natsUtil.pushAlert(alertString);
        }
    }

    /**
     * 释放资源
     * @return 资源是否释放成功
     */
    public boolean close() {

        natsUtil.close();
        alertRuleUtil.close();

        return true;
    }

    public ProbeAlert() {}

}
