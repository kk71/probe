package com.yamu.bigdata.product.probe.sample.model;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import java.util.ArrayList;

/**
 * NS相关的dns section list
 */
public class ProbeResultDnsSectionListNs extends ProbeResultDnsSectionList{

    @Override
    public void setSections(JSONArray sectionInJsonObject) {
        for (Object a: sectionInJsonObject) {
            JSONObject anOriginalSection = (JSONObject) a;
            ProbeResultDnsSectionNs aSection = new ProbeResultDnsSectionNs();
            aSection.name = anOriginalSection.getString("name");
            aSection.result = anOriginalSection.getString("result");
            aSection.rdclass = anOriginalSection.getString("rdclass");
            aSection.ttl = anOriginalSection.getInteger("ttl");
            aSection.rdtype = anOriginalSection.getString("rdtype");

            // 设置下级NS的A记录
            aSection.resultsA = new ArrayList<>();
            aSection.setResultsA(anOriginalSection.getJSONArray("results_a"));

            this.sections.add(aSection);
        }
    }

}
