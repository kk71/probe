package com.yamu.bigdata.product.probe.sample.model;

import com.alibaba.fastjson.JSONArray;

/**
 * 任务类型
 * 目前任务类型是个array of two string，需要提供序列化功能以兼容老版本的方式写入es，
 * 即写入拼接好的文本
 */
public class TaskType {

    private final String t1;
    private final String t2;

    /**
     * 初始化任务类型
     * @param t1
     * @param t2
     */
    public TaskType(String t1, String t2) {
        this.t1 = t1;
        this.t2 = t2;
    }

    /**
     * 初始化任务类型，从JsonArray读取
     * @param taskType
     */
    public TaskType(JSONArray taskType) {
        this.t1 = taskType.getString(0);
        this.t2 = taskType.getString(1);
    }

    public String serializeForEs() {
        return String.format("%s-%s", t1, t2);
    }

    /**
     * 重载比较方法
     * @param anotherTaskType
     * @return
     */
    public boolean equals(TaskType anotherTaskType) {
        return anotherTaskType.serializeForEs().equals(this.serializeForEs());
    }

}
