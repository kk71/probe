package com.yamu.bigdata.product.probe.sample.utils;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import okhttp3.*;
import redis.clients.jedis.params.SetParams;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * 给大数据专门开发的，出网信息缓存
 * 出网信息源是：http://192.168.6.125:55303/service/system/dimtable/ips/ipList/v1
 * 具体参见：http://confluence.yamu.com/pages/viewpage.action?pageId=4277830
 * 按照省-市-运营商的方式查询该区域的网内IP集合，然后跟DNS解析到的记录匹配。如果解析值不在IP集合内，则出网告警。
 * IP集合目前1周过期
 */
public class RedisConnectorOutNet extends RedisConnector {

    // http API的IP
    protected String apiHostPort;
    protected String apiHost;
    protected Integer apiPort;
    // http API请求的token
    protected String apiHeaderToken;
    // 过期时间
    protected Integer ExpiringTime;
    // 过期时间(针对空数据)
    protected Integer ExpiringTimeEmpty;

    protected OkHttpClient httpClient = new OkHttpClient();

    public RedisConnectorOutNet() {
        ConfigUtil configUtil = new ConfigUtil();
        this.apiHostPort = configUtil.getValueByKey("OutNet.HttpHostPort");
        this.apiHost = this.apiHostPort.split(":")[0];
        this.apiPort = Integer.parseInt(this.apiHostPort.split(":")[1]);
        this.apiHeaderToken = configUtil.getValueByKey("OutNet.HttpHeaderToken");
        this.ExpiringTime = Integer.parseInt(configUtil.getValueByKey("OutNet.ExpiringTime"));
        this.ExpiringTimeEmpty = Integer.parseInt(configUtil.getValueByKey("OutNet.ExpiringTimeEmpty"));
        this.db_id = 9;
        this.init();
    }

    /**
     * 从http API请求数据
     * @param country
     * @param province
     * @param city
     * @param carrier
     * @return
     */
    protected synchronized ArrayList<String> queryThroughAPI(
            String country, String province, String city, String carrier) {
        ArrayList<String> ret = new ArrayList<>();
        HttpUrl.Builder urlBuilder = new HttpUrl.Builder()
                .scheme("http")
                .host(this.apiHost)
                .port(this.apiPort)
                .addPathSegments("service/system/dimtable/ips/ipList/v1");
        urlBuilder.addQueryParameter("country", country);
        urlBuilder.addQueryParameter("province", province);
        if (city!=null&&city.length()>0) {
            urlBuilder.addQueryParameter("city", city);
        }
        if (carrier!=null&&carrier.length()>0) {
            urlBuilder.addQueryParameter("isp", carrier);
        }
        HttpUrl httpUrl = urlBuilder.build();
        Request request = new Request.Builder().
                url(httpUrl)
                .header("x-auth-token", this.apiHeaderToken).get().build();
        String body = "[]";
        try (Response response = this.httpClient.newCall(request).execute()) {
            body = response.body().string();
        } catch (IOException e) {
            logger.error(e.getMessage());
        }
        JSONArray jsonArray;
        try {
            jsonArray = JSON.parseArray(body);
        } catch (Exception e) {
            jsonArray = new JSONArray();
        }
        ret = (ArrayList<String>) jsonArray.toJavaList(String.class);
        logger.info(ret.toString());
        return ret;
    }

    /**
     * 查询IP集合
     * @param province
     * @return
     */
    public ArrayList<String> query(String province, String city, String carrier) {
        String key = String.format("%s-%s-%s", province, city, carrier);
        String cachedIpSetJsonString = jedis.get(key);
        if (cachedIpSetJsonString==null||cachedIpSetJsonString.isEmpty()) {
            ArrayList<String> list = queryThroughAPI("中国", province, city, carrier);
            String jsonString = JSONArray.toJSONString(list);
            SetParams setParams = new SetParams();
            if (list==null||list.size()==0) {
                setParams.ex(this.ExpiringTimeEmpty);
            } else {
                setParams.ex(this.ExpiringTime);
            }
            jedis.set(key, jsonString, setParams);
            cachedIpSetJsonString = jsonString;
        }
        JSONArray jsonArray = JSONArray.parseArray(cachedIpSetJsonString);
        List<String> ips = jsonArray.toJavaList(String.class);
        return (ArrayList<String>) ips;
    }

    public ArrayList<String> query() {
        return this.query("", "", "中国电信");
    }

}
