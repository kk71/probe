package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.TaskType;

import java.util.List;

/**
 * http speedup拨测的统计分析记录
 */
public class EsHttpSpeedup {

    public TaskType task_type;

    public String task_id;

    public String task_probing_id;

    public String create_time;

    public List<EsHttpSpeedupBestChoice> best_choices;

}
