package com.yamu.bigdata.product.probe.conf;

import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import static org.junit.jupiter.api.Assertions.*;

class ConfigUtilTest {
    ConfigUtil configUtil = new ConfigUtil();

    @org.junit.jupiter.api.Test
    /**
     * 测试获取key
     */
    void getValueByKey() {
        assertEquals("test", configUtil.getValueByKey("test.flag"));

    }

    @org.junit.jupiter.api.Test
    /**
     * 测试通过前缀获取ProperTIES格式配置
     */
    void getPropertiesByPrefix() {

        Properties configs = new Properties();
        configs.put("flag", "test");
        configs.put("num", "3");

        assertEquals(configs, configUtil.getPropertiesByPrefix("test"));
    }

    @org.junit.jupiter.api.Test
    /**
     * 测试通过前缀获取Map格式配置
     */
    void getMapByPrefix() {
        Map<String, String> configs = new HashMap<String, String>();
        configs.put("flag", "test");
        configs.put("num", "3");

        assertEquals(configs, configUtil.getMapByPrefix("test"));

    }
}