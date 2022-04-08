package com.yamu.bigdata.product.probe.sample.bridge;

import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.sync.DataSourceCallBack;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.UUID;

public class EmqXSub {

    private static final Logger logger = LoggerFactory.getLogger(EmqXSub.class);
    private final String uuid = UUID.randomUUID().toString();
    private String clientId = null;

    private void init() {

        ConfigUtil configUtil = new ConfigUtil();

        // 参数配置
        String topic = configUtil.getValueByKey("mq.client.emqx.subtopic");
        String url = configUtil.getValueByKey("mq.client.emqx.url");
        if (clientId == null) {
            clientId = configUtil.getValueByKey("mq.client.emqx.subClientId")+uuid;
        }

        String user_name = configUtil.getValueByKey("mq.client.emqx.user_name");
        String password = configUtil.getValueByKey("mq.client.emqx.password");

        MemoryPersistence persistence = new MemoryPersistence();

        boolean isNotConnect=true;
        MqttClient client = null;
        // 若链接不成功，自动重连至成功
        while (isNotConnect){
            try {
                client = new MqttClient(url, clientId, persistence);

                // MQTT 连接选项
                MqttConnectOptions connOpts = new MqttConnectOptions();
                connOpts.setUserName(user_name);
                connOpts.setPassword(password.toCharArray());
                // 保留会话f
                connOpts.setCleanSession(true);
                // 设置回调s
                client.setCallback(new DataSourceCallBack());
                // 建立连接
                System.out.println("Connecting to broker: " + url);

                client.connect(connOpts);

                System.out.println("Connected");

                System.out.println("start subscribe topic:" + topic);

                // 订阅消息
                client.subscribe(topic);

                isNotConnect = false;

            }
            catch (MqttException me) {
                System.out.println("reason " + me.getReasonCode());
                System.out.println("msg " + me.getMessage());
                System.out.println("loc " + me.getLocalizedMessage());
                System.out.println("cause " + me.getCause());
                System.out.println("excep " + me);
                me.printStackTrace();

                // 10分后钟重连
                try {
                    Thread.sleep(1*600*1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                logger.info("will reconnect emqx...");
            }catch (Exception e){
                e.printStackTrace();
            }finally {

            }
        }
    }


    public EmqXSub(String clientId) {
        this.clientId = clientId;
        init();
    }
}
