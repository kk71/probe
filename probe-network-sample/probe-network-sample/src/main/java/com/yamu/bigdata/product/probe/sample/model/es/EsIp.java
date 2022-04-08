package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.GeoPoint;
import com.yamu.bigdata.product.probe.sample.utils.IpdbUtil;

import java.io.FileNotFoundException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 统一的标注一个IP的地理运营商信息的数据结构
 */
public class EsIp {

    // IP
    private String ip;

    // 所在国家
    private String country_id;
    private String country;

    // 所在省
    private String province_id;
    private String province;

    // 所在市
    private String city_id;
    private String city;

    // 所在运营商
    private String carrier;

    // 地理位置唯一标识
    public String location_id;

    // GPS信息[维度、经度]
    private GeoPoint gps;

    public String getIp() {
        return ip;
    }

    /**
     *
     * @param ip
     */
    public void setIp(String ip) {
        this.ip = ip;
        loadIpInfo();
    }

    /**
     * 计算location_id
     */
    public String setLocationId() {
        this.location_id = String.format("%s-%s-%s-%s",
                this.country_id, this.province_id, this.city_id, this.carrier);
        return this.location_id;
    }

    // 装载ip信息

    /**
     * ["0国家","1省","2城市","3","4运营商","5维度","6经度","7UTC时区","8UTC时区","9城市编码","10国家编码","11语言","12AP"]
     */
    private void loadIpInfo(){

        //如果是IPV6返回
        String regex = "\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}";
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(ip);
        if (!matcher.matches()) {
            return;
        }
        try {
            String[] ipInfo = IpdbUtil.queryByIp(ip, "CN");
            this.country_id = ipInfo[10];
            this.country = ipInfo[0];
            try {
                if (ipInfo[9].length() > 3) {
                    this.province_id = ipInfo[9].substring(0, 3) + "000";
                }
            } catch (Exception e) {
                e.printStackTrace();
                System.out.println(ipInfo[9]);
            }
            this.province = ipInfo[1];
            this.city_id = ipInfo[9];
            this.city = ipInfo[2];
            this.carrier = ipInfo[4];
            GeoPoint geo = new GeoPoint();
            geo.lat = Float.parseFloat(ipInfo[5]);
            geo.lon = Float.parseFloat(ipInfo[6]);
            this.gps = geo;
            this.city = ipInfo[2];
            // calculate location_id
            setLocationId();
        } catch (FileNotFoundException e) {
            System.out.println("IPDB info generation failed, since the IPDB database file was not found.");
        }
    }

    public String getCountry_id() {
        return country_id;
    }

    public void setCountry_id(String country_id) {
        this.country_id = country_id;
        setLocationId();
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public String getProvince_id() {
        return province_id;
    }

    public void setProvince_id(String province_id) {
        this.province_id = province_id;
        setLocationId();
    }

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public String getCity_id() {
        return city_id;
    }

    public void setCity_id(String city_id) {
        this.city_id = city_id;
        setLocationId();
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getCarrier() {
        return carrier;
    }

    public void setCarrier(String carrier) {
        this.carrier = carrier;
        setLocationId();
    }

    public GeoPoint getGps() {
        return gps;
    }

    public void setGps(GeoPoint gps) {
        this.gps = gps;
    }

    public EsIp(String ip) {
        this.ip = ip;
        loadIpInfo();
    }

    public EsIp() {}

}
