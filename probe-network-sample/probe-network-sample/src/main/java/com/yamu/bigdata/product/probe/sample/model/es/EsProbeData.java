package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.ProbeDevice;
import com.yamu.bigdata.product.probe.sample.model.ProbeResult;
import com.yamu.bigdata.product.probe.sample.model.ProbeTask;

/**
 * es拨测结果数据
 */
public class EsProbeData {

    // 任务id
    public String task_id;

    // 任务下发id，即本次执行任务的id
    public String task_probing_id;

    // 任务类型
    public String task_type;

    // 用户组id
    public String gid;

    // 设备id
    public String client_id;

    // 设备客户端版本号
    public String client_version;

    // 设备ip信息
    public EsIp client_ip;

    // 设备时区
    public String timezone;

    // gps信息:[latitude,longitude]
    public String[] gps;

    // 拨测任务执行状态
    public String probe_task_status;

    // 任务创建时间
    @Deprecated
    public String create_time;

    // 任务失效时间
    @Deprecated
    public String expiration_time;

    // 任务发送时间
    public String task_send_time;

    // 任务接收时间
    public String receive_time;

    // 任务执行时间
    @Deprecated
    public String start_time;

    // 任务完成时间
    @Deprecated
    public String end_time;

    // 数据上报时间
    public String push_time;

    // dns服务器ip信息
    public EsIp dns_server_ip;

    /**
     * 写入任务信息
     * @param probeTask
     * @return
     */
    public void putTask(String taskProbingId, ProbeTask probeTask) {
        this.task_id = probeTask.taskId;
        this.task_probing_id = taskProbingId;
        this.task_type = probeTask.taskType.serializeForEs();
        this.gid = probeTask.gid;
        this.create_time = probeTask.createTime;
        this.task_send_time = probeTask.taskSendTime;
        this.receive_time = probeTask.receiveTime;
        this.start_time = probeTask.startTime;
        this.push_time = probeTask.pushTime;
    }

    /**
     * 写入设备信息
     * @param probeDevice
     * @return
     */
    public void putProbeDevice(ProbeDevice probeDevice) {
        this.client_id=probeDevice.getClient_id();
        this.client_version=probeDevice.getClient_version();
        this.client_ip=probeDevice.getClient_ip();
        this.timezone=probeDevice.getTimezone();
        this.gps=probeDevice.getGps();
    }

    /**
     * 写入结果信息
     * @param probeResult
     * @return
     */
    public void putProbeResult(ProbeResult probeResult) {
        this.probe_task_status = probeResult.probeTaskStatus;
    }

    public EsProbeData(String taskProbingId,
                       ProbeTask probeTask,
                       ProbeDevice probeDevice,
                       ProbeResult probeResult) {
        this.putProbeDevice(probeDevice);
        this.putTask(taskProbingId, probeTask);
        this.putProbeResult(probeResult);
    }

    public EsProbeData() {}
}
