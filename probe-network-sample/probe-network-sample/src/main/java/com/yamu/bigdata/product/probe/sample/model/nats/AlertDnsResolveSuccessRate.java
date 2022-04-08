package com.yamu.bigdata.product.probe.sample.model.nats;


import java.text.NumberFormat;

/**
 * 告警数据结构：dns的特殊告警：解析成功率
 * 特点：拨测的是域名列表
 * batchID:同一拨测任务下不同批次ID
 */
public class AlertDnsResolveSuccessRate extends AlertDns {

    // task_probing_id
    // 之前是results.uuid，
    // 每个拨测任务的一次拨测的结果可能分多个emqx消息发送，该id标识了多个拨测结果是同一次拨测
    public String uuid;

    public String succeess_rate;

    public Integer domain_group_length;

    public Integer total_probe_count;

    public Integer success_probe_count;


    /**
     * 计算并且设置成功率
     */
    public void calculateSuccessRate() {
        if (total_probe_count >= domain_group_length) {
            NumberFormat numberFormat = NumberFormat.getInstance();
            numberFormat.setMaximumFractionDigits(4);
            this.succeess_rate = numberFormat.format(
                    this.success_probe_count / (float) this.total_probe_count * 100) + "%";
        }
    }
}
