package com.yamu.bigdata.product.probe.sample.utils;

import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import redis.clients.jedis.Jedis;

/**
 * redis连接
 */
public abstract class RedisConnector {

    protected static final Logger logger = LoggerFactory.getLogger(RedisConnector.class);
    protected ConfigUtil configUtil = new ConfigUtil();
    protected final String host = configUtil.getValueByKey("redis.server.host");
    protected final int port = Integer.parseInt(configUtil.getValueByKey("redis.server.port"));
    protected final String password = configUtil.getValueByKey("redis.server.password");
    protected int db_id;
    public Jedis jedis = null;

    protected void init() {
        // 连接 Redis 服务
        jedis = new Jedis(host, port);
        jedis.auth(password);
        jedis.select(this.db_id);

        // 测试redis服务连通性
        if (jedis.ping() == null) {
            logger.error("redis connect to " + host + ":" + port + " faild!");
        }
    }

    // 释放资源
    public boolean close(){
        jedis.close();
        return true;
    }

}
