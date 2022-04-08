package com.yamu.bigdata.product.probe.sample.utils;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.model.AlarmRule;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 *
 */
public class AlertRuleUtil {
    /////////////////////////////////////
    private static final Logger logger = LoggerFactory.getLogger(AlertRuleUtil.class);

    // 工具类
    ConfigUtil configUtil = new ConfigUtil();
    RedisConnectorAlarmRule redisConnector = new RedisConnectorAlarmRule();

    /////////////////////////////////////
    // 参数
    private final String alarm_types = configUtil.getValueByKey("alert.rule.alarm_types");

    /////////////////////////////////////

//    // 获取数据
//    public Map<String, Map<String, Object>> getAlertRulesByTaskId(String task_id) {
//        Map<String, Map<String, Object>> rules = new HashMap<>();
//
//        String alert_rules = redisUtil.query(ruleDb, task_id);
//        rules = (Map<String, Map<String, Object>>) JSON.parse(alert_rules);
//
//        return rules;
//    }

    // 获取数据
    public List<AlarmRule> getAlertRulesByTaskId(String task_id) {

        String rules = redisConnector.query(task_id);

        // 取规则
        Iterator<Object> ruleIterator = JSON.parseArray(rules).iterator();
        List<AlarmRule> rulesList = new ArrayList<>();
        AlarmRule alarmRule = null;

        while (ruleIterator.hasNext()) {
            // 取规则集合
            JSONObject typeRule = (JSONObject) ruleIterator.next();
            Iterator<Object> rulesIterator = typeRule.getJSONArray("rules").iterator();

            // 封装规则
            while (rulesIterator.hasNext()) {

                JSONObject rule = (JSONObject) rulesIterator.next();
                alarmRule = new AlarmRule();

                alarmRule.setId(rule.getString("id"));
                alarmRule.setField(rule.getString("field"));
                alarmRule.setOp(rule.getString("op"));

                // 取values
                JSONArray v = rule.getJSONArray("value");
                if (null != v) {
                    Object[] values = v.toArray();
                    String[] myvalues = new String[values.length];
                    for (int i = 0; i < values.length; i++) {
                        myvalues[i] = (String) values[i];
                    }
                    alarmRule.setValue(myvalues);
                }
                // 设置告警类型
                alarmRule.setAlert_type(typeRule.getString("alert_type"));

                rulesList.add(alarmRule);
            }
        }

        return rulesList;
    }

    // 释放资源
    public void close() {
        redisConnector.close();
    }
}
