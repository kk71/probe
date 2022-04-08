package com.yamu.bigdata.product.probe.sample;

import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.bridge.EmqXSub;
import org.apache.commons.lang3.concurrent.BasicThreadFactory;

import java.util.UUID;
import java.util.concurrent.*;

public class Main {
    public static void main(String[] args) {

        ConfigUtil configUtil = new ConfigUtil();
        final String clientId = configUtil.getValueByKey("mq.client.emqx.subClientId");
        int threadNum = Integer.parseInt(configUtil.getValueByKey("thread.pool.subscribe.threadNum"));

        ThreadFactory factory = new BasicThreadFactory.Builder().namingPattern("probe-thread-").build();
        ExecutorService emqxSubThreadPool = new ThreadPoolExecutor(
                threadNum,
                threadNum,
                5,
                TimeUnit.SECONDS,
                new LinkedBlockingQueue<>(threadNum),
                factory
        );

        for (int i = 0; i < threadNum; i++) {
            // 异步发送原始数据
            emqxSubThreadPool.submit(new Callable<Long>() {
                                         @Override
                                         public Long call() throws Exception {
                                             EmqXSub emqXSub = new EmqXSub(clientId + UUID.randomUUID());
                                             return 0L;
                                         }
                                     }
            );
        }
    }
}
