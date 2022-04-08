package com.yamu.bigdata.product.probe.sample.model;

/**
 * dns拨测结果的section：answer_section, authority_section, additional_section的结构
 */
public class ProbeResultDnsSection {

    // 值
    public String name;

    // 过期时间
    public Integer ttl;

    public String rdclass;

    // 值类型（如A CNAME..
    public String rdtype;

    // 拨测结果
    public String result;

}
