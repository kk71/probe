package com.yamu.bigdata.product.probe.sample.model.nats;

/**
 * dns NS监控A记录告警
 */
public class AlertDnsNs extends AlertDns{

    /**
     * A记录的实际值
     */
    public String[] answer_results_a;

}
