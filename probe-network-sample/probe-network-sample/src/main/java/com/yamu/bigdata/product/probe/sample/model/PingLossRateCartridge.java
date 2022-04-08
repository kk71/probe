package com.yamu.bigdata.product.probe.sample.model;

import java.util.ArrayList;
import java.util.Date;

/**
 * 用以统计丢包率的仓库
 */
public class PingLossRateCartridge {

    // 丢包率统计的标识位个数
    public static Integer calcCount = 10;

    // 拨测端id
    public String clientId;

    // 拨测目标
    public String destination;

    // 丢包标志位
    protected ArrayList<PingLossRateSignature> lossSignatures;

    public PingLossRateCartridge() {
        this.lossSignatures = new ArrayList();
    }

    /**
     * 初始化一个统计丢包率的仓库
     * @param clientId
     * @param destination
     */
    public PingLossRateCartridge(String clientId, String destination) {
        this();
        this.clientId = clientId;
        this.destination = destination;
    }

    /**
     * 增加标识位
     * @param s 是否丢包了
     */
    public void addSignature(Boolean s) {
        PingLossRateSignature pingLossRateSignature = new PingLossRateSignature(s, new Date());
        this.lossSignatures.add(pingLossRateSignature);
        while (this.lossSignatures.size() > calcCount) {
            this.lossSignatures.remove(0);
        }
    }

    /**
     * 计算当前丢包率
     * @return
     */
    public Double getLossRate() {
        if (this.lossSignatures.size() < calcCount) {
            return 0.0;  // 如果丢包标识位个数没到达要求的calcCount个数，则认为丢包率为0
        }
        Integer lossSignatures = 0;
        for (PingLossRateSignature lossRateSignature: this.lossSignatures) {
            if (lossRateSignature.lossOrNot) {
                lossSignatures += 1;
            }
        }
        return lossSignatures.doubleValue() / calcCount;
    }

}
