package com.yamu.bigdata.product.probe.sample.model.nats;

import com.yamu.bigdata.product.probe.sample.model.Target;

/**
 * 告警数据结构：基类
 */
public class Alert {

    // 告警类型
    public String alarmType;

    // 拨测设备标识
    public String alarmObject;

    // 任务标识
    public String task_id;

    // 目标
    public Target target;

    // 创建时间
    public String add_time;

    // 任务执行状态
    public String probe_task_status;

}
