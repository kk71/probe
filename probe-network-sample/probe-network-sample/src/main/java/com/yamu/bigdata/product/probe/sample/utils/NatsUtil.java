package com.yamu.bigdata.product.probe.sample.utils;

import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import io.nats.client.Connection;
import io.nats.client.Nats;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

public class NatsUtil {

    private static final Logger logger = LoggerFactory.getLogger(NatsUtil.class);
    // 参数定义
    private String topic = null;
    private String user_name = null;
    private String password = null;
    private long sleeptime = 10;
    private String broker = null;

    private Connection nc = null;

    // 初始化
    private void init() {
        ConfigUtil configUtil = new ConfigUtil();

        // 参数配置
        topic = configUtil.getValueByKey("mq.client.nats.pubtopic");
        user_name = configUtil.getValueByKey("mq.client.nats.user_name");
        password = configUtil.getValueByKey("mq.client.nats.password");
        sleeptime = Long.parseLong(configUtil.getValueByKey("mq.client.nats.sleeptime"));
        broker = "nats://" + user_name + ":" + password + "@" + configUtil.getValueByKey("mq.client.nats.broker") + ":" + configUtil.getValueByKey("mq.client.nats.port");

        // 初始化客户端
        try {
            nc = Nats.connect(broker);
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * 发送告警
     * @param alert
     */
    public void pushAlert(String alert) {

        try {
            // 转json
            String msgs = alert;

            // 发布消息
            nc.publish(topic, msgs.getBytes(StandardCharsets.UTF_8));

            try {
                Thread.sleep(sleeptime);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            // 刷新消息
            nc.flush(Duration.ZERO);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }


    // 释放资源
    public boolean close(){

        try {
            nc.close();
        } catch (InterruptedException e) {
            e.printStackTrace();
            return false;
        }

        logger.info("nats client closed!");
        return true;
    }


    public NatsUtil() {
        init();
    }
}
