package com.yamu.bigdata.product.probe.sample.model;

import java.util.List;

/**
 * 任务对象
 */
public class ProbeTask {

    // 任务标识
    public String taskId;

    // 任务类型
    public TaskType taskType;

    // 用户组id
    public String gid;

    // 任务创建时间
    @Deprecated
    public String createTime;

    // 任务发送时间
    public String taskSendTime;

    // 任务接收时间
    public String receiveTime;

    // 拨测端任务执行开始时间
    @Deprecated
    public String startTime;

    // 拨测结果数据从拨测端上报的时间
    public String pushTime;

    // 拨测目标信息
    public List<Target> targets;
    
}
