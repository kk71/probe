package com.yamu.bigdata.product.probe.sample.result.handler;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.sample.alert.ProbeAlert;
import com.yamu.bigdata.product.probe.sample.model.*;
import com.yamu.bigdata.product.probe.sample.model.es.EsProbeData;
import com.yamu.bigdata.product.probe.sample.sync.DataSourceCallBack;
import com.yamu.bigdata.product.probe.sample.utils.DtUtil;
import com.yamu.bigdata.product.probe.sample.utils.DeviceInfoUtil;
import com.yamu.bigdata.product.probe.sample.utils.EsUtil;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * 拨测结果处理类
 * 根据结果归属的任务类型，分别继承，分别处理
 */
public abstract class ResultHandler {

    protected static Logger logger = LoggerFactory.getLogger(DataSourceCallBack.class);

    static EsUtil esUtil = new EsUtil(EsUtil.esIndexProbedata);

    protected ConfigUtil configUtil = new ConfigUtil();
    private final String dataIndex = configUtil.getValueByKey("es.data.index");
    private String currentIndexName = null;

    protected ProbeAlert probeAlert; // 根据具体使用哪个告警类初始化
    protected DeviceInfoUtil deviceInfoUtil = new DeviceInfoUtil();
    protected ExecutorService parseThreadPool = null;
    protected ExecutorService alertThreadPool = null;
    protected ExecutorService syncThreadPool = null;

    protected String taskProbingId;  // 本次执行任务的id
    protected ProbeTask probeTask;
    protected ProbeDevice probeDevice;
    protected ArrayList<ProbeResult> probeResults;

    /**
     * 线程数
     */
    int syncThreadNum = Integer.parseInt(configUtil.getValueByKey("thread.pool.sync.threadNum"));
    int alertThreadNum = Integer.parseInt(configUtil.getValueByKey("thread.pool.alert.threadNum"));
    int parseThreadNum = Integer.parseInt(configUtil.getValueByKey("thread.pool.parse.threadNum"));

    /**
     * 平稳地结束线程池
     * Ref: https://www.twle.cn/c/yufei/javatm/javatm-basic-executorservice.html
     * @param pool
     */
    private void closeThreadPool(ExecutorService pool) {
        try {
            pool.shutdown();

            if(!pool.awaitTermination(3, TimeUnit.SECONDS)){
                pool.shutdownNow();
            }
        } catch (InterruptedException e) {
            System.out.println("awaitTermination interrupted: " + e);
            pool.shutdownNow();
        }
    }

    public ResultHandler(JSONObject originalJsonResult){

        // 创建索引
        currentIndexName = EsUtil.getEsDailyIndexName(dataIndex);
        esUtil.createIndexIfNotExists(currentIndexName);

        // 初始化线程池
        if (parseThreadPool == null) {
            parseThreadPool = Executors.newFixedThreadPool(parseThreadNum);
        }
        if (alertThreadPool == null) {
            alertThreadPool = Executors.newFixedThreadPool(alertThreadNum);
        }
        if (syncThreadPool == null) {
            syncThreadPool = Executors.newFixedThreadPool(syncThreadNum);
        }

        // 一次拨测任务可能分多次EMQX消息进行发送，该id标识了两条EMQX消息属于同一个任务的输出
        // 即：老代码中的results.uuid
        this.taskProbingId = originalJsonResult.getString("task_probing_id");

        // 任务信息
        JSONObject task = originalJsonResult.getJSONObject("task");
        this.probeTask = this.packTask(task);

        // 设备信息
        JSONObject device = originalJsonResult.getJSONObject("device");
        this.probeDevice = deviceInfoUtil.getEsDeviceByDeviceInfo(device);

        // 结果信息
        JSONArray results = originalJsonResult.getJSONArray("results");
        this.probeResults = new ArrayList<ProbeResult>();
        for (Object result: results) {
            ProbeResult probeResult = this.packResult((JSONObject) result);
            probeResults.add(probeResult);
        }
        ArrayList<EsProbeData> esTasks = this.packEsTask();

        // 异步告警，按照任务类型分发给不同的告警类去处理
        alertThreadPool.submit(() -> {
            return this.alertRunInThread(
                    this.taskProbingId, this.probeTask, probeDevice.getClient_id(), probeResults);
        });

        try {
            for (EsProbeData esTask: esTasks) {
                // 写入es
                String indexName = EsUtil.getEsDailyIndexName(dataIndex);
                if (!indexName.equals(currentIndexName)) {
                    esUtil.createIndexIfNotExists(indexName);
                    currentIndexName = indexName;
                }
                parseThreadPool.submit(() -> {
                            long start = System.currentTimeMillis();
                            Map map = (Map<String, Object>) JSON.toJSON(esTask);
                            esUtil.bulkSubmit(map, currentIndexName);
                            return System.currentTimeMillis() - start;
                        }
                );
            }
        } catch (Exception e) {
            e.printStackTrace();
            logger.error(e.getMessage());
        }
        this.closeThreadPool(parseThreadPool);
        this.closeThreadPool(alertThreadPool);
        this.closeThreadPool(syncThreadPool);
        this.taskIsDone();
    }

    /**
     * 当前任务写入结束之后执行善后操作
     */
    protected void taskIsDone() {}

    public ResultHandler(){}

    /**
     * 封装任务信息
     * @param task
     * @return
     */
    public ProbeTask packTask(JSONObject task) {
        String taskId = task.getString("task_id");

        JSONArray taskTypeArray = task.getJSONArray("task_type");
        TaskType taskType = new TaskType(
                taskTypeArray.getString(0), taskTypeArray.getString(1));

        ProbeTask probeTask = new ProbeTask();
        probeTask.taskId = taskId;
        probeTask.taskType = taskType;
        probeTask.gid = task.getString("gid");
        probeTask.createTime = DtUtil.localToUtc(task.getString("task_send_time"));
        probeTask.taskSendTime = DtUtil.localToUtc(task.getString("task_send_time"));
        probeTask.receiveTime = DtUtil.localToUtc(task.getString("task_receive_time"));
        probeTask.startTime = DtUtil.localToUtc(task.getString("task_receive_time"));
        probeTask.pushTime = DtUtil.localToUtc(task.getString("task_push_time"));
        probeTask.targets = this.packTargets(task);
        return probeTask;
    }

    /**
     * 封装emqx传来的拨测结果
     * @param result
     * @return
     */
    public abstract ProbeResult packResult(JSONObject result);

    /**
     * 封装本次拨测的全部拨测结果。具体是拆分成多个es文档，还是单一文档，还是任意拆分，以业务逻辑为准
     * @return 返回是列表！！
     */
    public abstract ArrayList<EsProbeData> packEsTask();

    /**
     * 异步发送告警的线程函数
     */
    public abstract Long alertRunInThread(
            String taskProbingId,
            ProbeTask task,
            String clientId,
            List<ProbeResult> results
    );

    /**
     * 封装task.target列表
     * @param task
     * @return
     */
    public abstract List<Target> packTargets(JSONObject task);

}
