package com.yamu.bigdata.product.probe.sample.utils;

/**
 * redis连接：存放拨测任务的告警规则
 */
public class RedisConnectorAlarmRule extends RedisConnector {

    RedisConnectorAlarmRule() {
        this.db_id = 0;
        this.init();
    }

    /**
     * 查询某个任务的规则信息
     * @param task_id
     * @return
     */
    public String query(String task_id) {
        return this.jedis.get(task_id);
    }

}
