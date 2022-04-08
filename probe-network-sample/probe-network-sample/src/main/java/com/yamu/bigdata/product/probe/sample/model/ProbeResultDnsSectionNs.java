package com.yamu.bigdata.product.probe.sample.model;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import java.util.ArrayList;

/**
 * NS解析特有的section结构
 */
public class ProbeResultDnsSectionNs extends ProbeResultDnsSection {

    public ArrayList<ProbeResultDns> resultsA;

    /**
     * 抓取results_A的结构，NOTICE:只抓取answer_section的
     * @param resultsAList
     */
    public void setResultsA(JSONArray resultsAList) {
        this.resultsA = new ArrayList<>();
        for (Object r: resultsAList) {
            JSONObject jsonObject = (JSONObject) r;
            JSONArray jsonArrayAnswerSection = jsonObject.getJSONArray("answer_section");
            ProbeResultDns probeResultDns = new ProbeResultDns();
            probeResultDns.answerSection = new ProbeResultDnsSectionList();
            probeResultDns.answerSection.setSections(jsonArrayAnswerSection);
            this.resultsA.add(probeResultDns);
        }
    }

}
