package com.yamu.bigdata.product.probe.conf;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

public class ConfigUtil {
    private static final Logger logger = LoggerFactory.getLogger(ConfigUtil.class);

    // 配置文件路径
    private String propertiesPath = null;

    // 配置文件s
    private Properties propts = new Properties();

    // 初始化配置文件
    public synchronized void init() {
        // 装配文件
        if (this.propertiesPath == null) {
            this.propertiesPath = System.getenv("bigdata_env");
            // 当环境变量为空时，默认为null
            if (this.propertiesPath == null) {
                this.propertiesPath = "-default";
            } else {
                this.propertiesPath = "-" + this.propertiesPath;
            }
        } else {
            this.propertiesPath = "-" + this.propertiesPath;
        }
        try {
            propts.load(this.getClass().getClassLoader().getResourceAsStream("application" + this.propertiesPath + ".properties"));
        } catch (Exception e) {
            e.printStackTrace();
            logger.error(e.getMessage());
        }
    }

    /**
     * 通过key获取value
     *
     * @param key
     * @return
     */
    public synchronized String getValueByKey(String key) {
        try {
            return propts.getProperty(key);
        } catch (Exception e) {
            e.printStackTrace();
            logger.error(e.getMessage());
            return null;
        }
    }

    /**
     * 通过前缀获取所有value
     *
     * @param prefix 前缀
     * @return
     */
    public synchronized Properties getPropertiesByPrefix(String prefix) {
        try {
            Properties properties = new Properties();
            prefix = prefix + ".";
            for (Object key : propts.keySet()) {
                if (key.toString().indexOf(prefix) > -1) {
                    properties.put(key.toString().substring(key.toString().indexOf(prefix) + prefix.length()), propts.get(key.toString()));
                }
            }
            logger.debug(">>> properties foreatch print:");
            for (Object o : properties.keySet()) {
                logger.debug("\t>" + o.toString() + ":" + properties.getProperty(o.toString()));
            }
            return properties;
        } catch (Exception e) {
            e.printStackTrace();
            logger.error(e.getMessage());
            return null;
        }
    }

    /**
     * 通过前缀获取所有value
     *
     * @param prefix 前缀
     * @return
     */
    public synchronized Map<String, String> getMapByPrefix(String prefix) {
        try {
            Map<String, String> map = new HashMap<String, String>();
            prefix = prefix + ".";
            for (Object key : propts.keySet()) {
                if (key.toString().indexOf(prefix) > -1) {
                    map.put(key.toString().substring(key.toString().indexOf(prefix) + prefix.length()), propts.get(key.toString()).toString());
                }
            }
            logger.debug(">>> properties foreatch print:");
            for (Object o : map.keySet()) {
                logger.debug("\t>" + o.toString() + ":" + map.get(o.toString()));
            }
            return map;
        } catch (Exception e) {
            e.printStackTrace();
            logger.error(e.getMessage());
            return null;
        }
    }

    public ConfigUtil(String propertiesPathIn) {
        this.propertiesPath = propertiesPathIn;
        // 初始化
        init();
    }

    //
    public ConfigUtil() {
        // 初始化
        init();
    }
}
