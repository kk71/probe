package com.yamu.bigdata.product.probe.sample.sync;

import com.alibaba.fastjson.JSON;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.bridge.EmqXSub;
import com.yamu.bigdata.product.probe.sample.utils.EsUtil;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 消息回调处理
 */
public class ProbeLogCallBack implements MqttCallback {


    private static final Logger logger = LoggerFactory.getLogger(ProbeLogCallBack.class);
    // 工具类声明
    EsUtil esUtil = new EsUtil(EsUtil.esIndexProbedata);
    ConfigUtil configUtil = new ConfigUtil();


    // 参数
    private final String log_index = configUtil.getValueByKey("es.log.index");
    // 线程数
    int sync_threadNum = Integer.parseInt(configUtil.getValueByKey("thread.log.sync.threadNum"));

    private final ExecutorService parseThreadPool = null;
    private final ExecutorService alertThreadPool = null;
    private ExecutorService syncThreadPool = null;


    @Override
    public void connectionLost(Throwable cause) {

        logger.warn("EmqX disconnected!The program will be reconnected in 10 seconds.");

        try {
            Thread.sleep(1*600*1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        ConfigUtil configUtil = new ConfigUtil();
        final String clientId = configUtil.getValueByKey("mq.log.emqx.subClientId");
        new EmqXSub(clientId + UUID.randomUUID());


        logger.info("EmqX reconnected!");

    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {

        if (syncThreadPool == null) {
            syncThreadPool = Executors.newFixedThreadPool(sync_threadNum);
        }

        // 发送原始数据
        String msgs = JSON.parse(new String(message.getPayload())).toString();
        logger.debug("receive data:"+JSON.toJSON(msgs));



        // 异步发送原始数据
        syncThreadPool.submit(new Callable<Long>() {
                                  @Override
                                  public Long call() throws Exception {
                                      long start = System.currentTimeMillis();
                                      esUtil.submit(msgs, log_index);
                                      return System.currentTimeMillis() - start;
                                  }
                              }
        );

        logger.info("source data submited!");

    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
        logger.info("deliveryComplete---------" + token.isComplete());
    }

}