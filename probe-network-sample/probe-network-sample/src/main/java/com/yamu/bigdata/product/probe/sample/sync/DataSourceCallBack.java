package com.yamu.bigdata.product.probe.sample.sync;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.bridge.EmqXSub;
import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.result.handler.*;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.UUID;

/**
 * 消息回调处理
 * @author wedo
 */
public class DataSourceCallBack implements MqttCallback {

    /**
     * 工具类声明
     */
    private static final Logger logger = LoggerFactory.getLogger(DataSourceCallBack.class);

    // 声明现有的全部任务类型
    private static final TaskType taskTypeDnsDnsHijack = new TaskType("dns", "dnsHijack");
    private static final TaskType taskTypeDnsDnsMonitor = new TaskType("dns", "dnsMonitor");
    private static final TaskType taskTypeDnsDnsPrefer = new TaskType("dns", "dnsPrefer");
    private static final TaskType taskTypeDnsDnsNSHijack = new TaskType("dns", "dnsNSHijack");
    private static final TaskType taskTypeDnsDnsResolve = new TaskType("dns", "dnsResolve");
    private static final TaskType taskTypeNetworkPing = new TaskType("network", "ping");
    private static final TaskType taskTypeNetworkTraceroute = new TaskType("network", "traceroute");
    private static final TaskType taskTypeResourcePageSpeedUp = new TaskType("resource", "pageSpeedUp");

    public DataSourceCallBack(){
    }

    @Override
    public void connectionLost(Throwable cause) {

        logger.warn(String.format(
                "EmqX disconnected!The program will be reconnected in 10 seconds: %s",
                cause.getMessage()
        ));

        cause.printStackTrace();

        try {
            Thread.sleep(10 * 1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        ConfigUtil configUtil = new ConfigUtil();
        final String clientId = configUtil.getValueByKey("mq.client.emqx.subClientId");
        new EmqXSub(clientId + UUID.randomUUID());

        logger.info("EmqX reconnected!");

    }

    @Override
    public void messageArrived(String topic, MqttMessage message) {

        // 打印原始数据
        String msgs = new String(message.getPayload());
        logger.debug("receive data: "+JSON.toJSON(msgs));
        JSONObject result = JSON.parseObject(msgs);

        JSONObject task = result.getJSONObject("task");
        String taskId = task.getString("task_id");
        JSONArray taskTypeArray = task.getJSONArray("task_type");
        TaskType taskType = new TaskType(
                taskTypeArray.getString(0), taskTypeArray.getString(1));
        logger.debug(String.format("task_id: %s, taskType: %s", taskId, taskType.serializeForEs()));

        if (taskType.equals(taskTypeDnsDnsHijack) |
                taskType.equals(taskTypeDnsDnsMonitor) |
                taskType.equals(taskTypeDnsDnsResolve) |
                taskType.equals(taskTypeDnsDnsPrefer)) {
            new ResultHandlerDns(result);
        } else if (taskType.equals(taskTypeDnsDnsNSHijack)) {
            new ResultHandlerDnsNs(result);
        } else if (taskType.equals(taskTypeNetworkPing)) {
            new ResultHandlerPing(result);
        } else if (taskType.equals(taskTypeNetworkTraceroute)) {
            new ResultHandlerTraceroute(result);
        } else if (taskType.equals(taskTypeResourcePageSpeedUp)) {
            new ResultHandlerHttpPageSpeedUp(result);
        } else {
            logger.error(String.format(
                    "coming result with unknown task_type: %s", taskType.serializeForEs()));
        }

    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
        logger.info("deliveryComplete---------" + token.isComplete());
    }

}