package com.yamu.bigdata.product.probe.sample.bridge;

import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.sync.DataSourceCallBack;
import com.yamu.bigdata.product.probe.sample.utils.MessageCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

public class EmqXBridge {
    public static void main(String[] args) {

        ConfigUtil configUtil = new ConfigUtil();

        // 参数配置
        String topic = configUtil.getValueByKey("mq.client.emqx.subtopic");
        String broker = "tcp://" + configUtil.getValueByKey("mq.client.emqx.broker") + ":" + configUtil.getValueByKey("mq.client.emqx.port");
        String clientId = configUtil.getValueByKey("mq.client.emqx.subClientId");
        String user_name = configUtil.getValueByKey("mq.client.emqx.user_name");
        String password = configUtil.getValueByKey("mq.client.emqx.password");
//        long timeout = Long.parseLong(configUtil.getValueByKey("mq.client.emqx.timeout"));
//        long sleeptime = Long.parseLong(configUtil.getValueByKey("mq.client.emqx.sleeptime"));

        MemoryPersistence persistence = new MemoryPersistence();

        try {
            MqttClient client = new MqttClient(broker, clientId, persistence);

            // MQTT 连接选项
            MqttConnectOptions connOpts = new MqttConnectOptions();
            connOpts.setUserName(user_name);
            connOpts.setPassword(password.toCharArray());
            // 保留会话f
            connOpts.setCleanSession(true);
            // 设置回调s
            client.setCallback(new DataSourceCallBack());
            // 建立连接
            System.out.println("Connecting to broker: " + broker);
            client.connect(connOpts);

            System.out.println("Connected");

            System.out.println("start subscribe topic:" + topic);

            // 订阅消息
            client.subscribe(topic);


        } catch (MqttException me) {
            System.out.println("reason " + me.getReasonCode());
            System.out.println("msg " + me.getMessage());
            System.out.println("loc " + me.getLocalizedMessage());
            System.out.println("cause " + me.getCause());
            System.out.println("excep " + me);
            me.printStackTrace();
        }
    }
}
