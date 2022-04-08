package com.yamu.bigdata.product.probe.sample.model;

import java.util.List;

/**
 * 域名列表拨测
 */
public class TargetDnsGroup extends TargetDns {

    // 域名列表id
    public Integer domainGroupId;

    // 域名列表
    public List<String> domains;

    // 域名列表名
    public String domainGroupName;

}
