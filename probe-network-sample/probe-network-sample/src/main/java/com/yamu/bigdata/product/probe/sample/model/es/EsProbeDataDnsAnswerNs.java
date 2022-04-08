package com.yamu.bigdata.product.probe.sample.model.es;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import java.util.ArrayList;

/**
 * NS监控的结构
 */
public class EsProbeDataDnsAnswerNs extends EsProbeDataDnsAnswer {

    /**
     * NS记录再次解析的A记录列表
     */
    public ArrayList<String> results_a;

    /**
     * @param ip
     */
    public EsProbeDataDnsAnswerNs(String ip) {
        super(ip);
    }

}
