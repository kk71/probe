package com.yamu.bigdata.product.probe.sample.utils;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.model.es.EsIp;
import com.yamu.bigdata.product.probe.sample.model.GeoPoint;
import com.yamu.bigdata.product.probe.sample.model.ProbeDevice;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;

/**
 * 根据设备id查询拨测点设备诶信息
 */
public class DeviceInfoUtil {

    private static final Logger logger = LoggerFactory.getLogger(DeviceInfoUtil.class);
    // db序号
    private int db_id = 5;

    // 初始化
    private void init() {

        ConfigUtil configUtil = new ConfigUtil();
        db_id = Integer.parseInt(configUtil.getValueByKey("info.device.redis.db"));

    }

    public ProbeDevice getEsDeviceByDeviceInfo(JSONObject data) {
        try {
            ProbeDevice esDevice = new ProbeDevice();
            JSONArray clientVersion = data.getJSONArray("client_version");
            esDevice.setClient_version(String.format("%d.%d.%d",
                    clientVersion.getInteger(0),
                    clientVersion.getInteger(1),
                    clientVersion.getInteger(2)
                    ));

            esDevice.setClient_id(data.getString("client_id"));

            JSONObject region = data.getJSONObject("region");

            // gps信息
            String[] gps = new String[2];
            gps[0] = region.getString("latitude");
            gps[1] = region.getString("longitude");
            esDevice.setGps(gps);

//            esDevice.setTimezone(data.getString("utc_offset"));
            // 设备ip信息
            EsIp esIp = new EsIp();
            if (StringUtils.isNotEmpty(region.getString("ip_address"))) {
                esIp.setIp(region.getString("ip_address"));
            }
            if (StringUtils.isNotEmpty(region.getString("country_name"))) {
                esIp.setCountry(region.getString("country_name"));
                esIp.setCountry_id(region.getString("country"));
            }
            if (StringUtils.isNotEmpty(region.getString("city_name"))) {
                esIp.setCity(region.getString("city_name"));
                esIp.setCity_id(region.getString("city"));
            }
            if (StringUtils.isNotEmpty(region.getString("province_name"))) {
                esIp.setProvince(region.getString("province_name"));
                esIp.setProvince_id(region.getString("province"));
            }
            String lon = region.getString("longitude");
            if (StringUtils.isNotEmpty(lon) && !"None".equals(lon)) {
                GeoPoint geo = new GeoPoint();
                geo.lat = Float.parseFloat(region.getString("latitude"));
                geo.lon = Float.parseFloat(lon);
                esIp.setGps(geo);
            }
            if (StringUtils.isNotEmpty(region.getString("carrier"))) {
                esIp.setCarrier(region.getString("carrier"));
            }
            esDevice.setClient_ip(esIp);

            return esDevice;
        } catch (NullPointerException e) {
            logger.error("device not exists! client_id:" + data.getString("uuid"));
            return null;
        }

    }

    public DeviceInfoUtil() {
        init();
    }
}
