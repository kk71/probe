package com.yamu.bigdata.product.probe.sample.model;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import java.util.ArrayList;

public class ProbeResultDnsSectionList {

    protected ArrayList<ProbeResultDnsSection> sections = new ArrayList<ProbeResultDnsSection>();

    /**
     * 设置section的值，从json结构解析
     * @param sectionInJsonObject
     */
    public void setSections(JSONArray sectionInJsonObject) {
        for (Object a: sectionInJsonObject) {
            JSONObject anOriginalSection = (JSONObject) a;
            ProbeResultDnsSection aSection = new ProbeResultDnsSection();
            aSection.name = anOriginalSection.getString("name");
            aSection.result = anOriginalSection.getString("result");
            aSection.rdclass = anOriginalSection.getString("rdclass");
            aSection.ttl = anOriginalSection.getInteger("ttl");
            aSection.rdtype = anOriginalSection.getString("rdtype");
            this.sections.add(aSection);
        }
    }

    public ArrayList<ProbeResultDnsSection> getSections() {
        return this.sections;
    }

    /**
     * 获取目前section中的全部A记录
     */
    public ArrayList<String> getSectionsWithRdtype(String rdtype) {
        ArrayList<String> r = new ArrayList<String>();
        for (ProbeResultDnsSection aSection: this.sections) {
            if (aSection.rdtype.equals(rdtype)) {
                r.add(aSection.result);
            }
        }
        return r;
    }

}
