package com.yamu.bigdata.product.probe.sample;

import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.bridge.EmqXLogSub;
import com.yamu.bigdata.product.probe.sample.bridge.EmqXSub;

import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainLog {
    public static void main(String[] args) {

        ConfigUtil configUtil = new ConfigUtil();
        final String clientId = configUtil.getValueByKey("mq.log.emqx.subClientId");
        int threadNum = Integer.parseInt(configUtil.getValueByKey("thread.log.subscribe.threadNum"));
        ExecutorService emqxSubThreadPool = Executors.newFixedThreadPool(threadNum);

        for (int i = 0; i < threadNum; i++) {
            // 异步发送原始数据
            emqxSubThreadPool.submit(new Callable<Long>() {
                                         @Override
                                         public Long call() throws Exception {
                                             EmqXLogSub emqXSub = new EmqXLogSub(clientId + UUID.randomUUID());
                                             return 0L;
                                         }
                                     }
            );
        }
    }
}
