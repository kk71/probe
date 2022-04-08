package com.yamu.bigdata.product.probe.sample.model;

import com.yamu.bigdata.product.probe.sample.model.es.EsIp;

public class ProbeDevice {
    // 设备id
    private String client_id;

    // 设备客户端版本号
    private String client_version;

    // 设备ip信息
    private EsIp client_ip;

    // 设备时区
    private String timezone;

    // gps信息:[latitude,longitude]
    private String[] gps;

    // 内网ip列表
    private String[] probe_ip_lan;

    public String getClient_id() {
        return client_id;
    }

    public void setClient_id(String client_id) {
        this.client_id = client_id;
    }

    public String getClient_version() {
        return client_version;
    }

    public void setClient_version(String client_version) {
        this.client_version = client_version;
    }

    public EsIp getClient_ip() {
        return client_ip;
    }

    public void setClient_ip(EsIp client_ip) {
        this.client_ip = client_ip;
    }

    public String getTimezone() {
        return timezone;
    }

    public void setTimezone(String timezone) {
        this.timezone = timezone;
    }

    public String[] getGps() {
        return gps;
    }

    public void setGps(String[] gps) {
        this.gps = gps;
    }

    public String[] getProbe_ip_lan() {
        return probe_ip_lan;
    }

    public void setProbe_ip_lan(String[] probe_ip_lan) {
        this.probe_ip_lan = probe_ip_lan;
    }

}
