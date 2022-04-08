package com.yamu.bigdata.product.probe.sample.model;

import java.util.Date;

/**
 * ping拨测丢包率统计用的标识位
 */
public class PingLossRateSignature {

    // 是否丢包了
    public Boolean lossOrNot;

    // 录入时间
    public Date dateTime;

    public PingLossRateSignature() {};

    public PingLossRateSignature(Boolean lossOrNot, Date datetime) {
        this.lossOrNot = lossOrNot;
        this.dateTime = datetime;
    }

}
