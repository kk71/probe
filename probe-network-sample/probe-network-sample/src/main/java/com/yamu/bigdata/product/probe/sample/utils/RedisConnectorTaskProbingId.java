package com.yamu.bigdata.product.probe.sample.utils;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONException;
import com.mysql.cj.xdevapi.JsonArray;
import com.mysql.cj.xdevapi.JsonString;

/**
 * redis连接：存放拨测成功的task_probing_id的列表
 */
public class RedisConnectorTaskProbingId extends RedisConnector {

    // 每个task_id下的list存放最多多少个task_probing_id，超过的旧task_probing_id即被舍弃
    private final int maxLength = 50;

    public RedisConnectorTaskProbingId() {
        this.db_id = 2;
        this.init();
    }

    /**
     * 增加新完成的task_probing_id
     * @param taskId
     * @param taskProbingId
     */
    public synchronized void insertNewTaskProbingId(String taskId, String taskProbingId) {
        String currentRedisListString = this.jedis.get(taskId);
        JSONArray currentRedisList;
        try{
            currentRedisList = (JSONArray) JSON.parse(currentRedisListString);
        } catch (JSONException e) {
            currentRedisList = new JSONArray();
        }
        if (currentRedisList==null) {
            currentRedisList = new JSONArray();
        }
        currentRedisList.add(0, taskProbingId);
        while (currentRedisList.size() > this.maxLength) {
            currentRedisList.remove(currentRedisList.size() - 1);
        }
        this.jedis.set(taskId, currentRedisList.toString());
    }

}
