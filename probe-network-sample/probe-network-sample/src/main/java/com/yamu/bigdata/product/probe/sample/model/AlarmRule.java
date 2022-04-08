package com.yamu.bigdata.product.probe.sample.model;

/**
 * 告警规则结构定义
 * {
 *       "id": 6,
 *       "field": "delay",
 *       "op": "gt",
 *       "value": [
 *         "200",
 *         "300"
 *       ]
 *     }
 */
public class AlarmRule {

    /**
     * 比较符号常量
     */
    // 大小，等价关系
    public static final String opGt = "gt";
    public static final String opLt = "lt";
    public static final String opEq = "eq";
    public static final String opNe = "ne";
    // 集合关系
    public static final String opIn = "in";
    public static final String opNotIn = "notin";
    public static final String opEmpty= "empty";

    // 规则标识
    private String id;
    // 处理字段
    private String field;
    // 操作符号
    private String op;
    // 匹配值
    private String[] value;
    // 告警类型
    private String alert_type;


    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getField() {
        return field;
    }

    public void setField(String field) {
        this.field = field;
    }

    public String getOp() {
        return op;
    }

    public void setOp(String op) {
        this.op = op;
    }

    public String[] getValue() {
        return value;
    }

    public void setValue(String[] value) {
        this.value = value;
    }

    public String getAlert_type() {
        return alert_type;
    }

    public void setAlert_type(String alert_type) {
        this.alert_type = alert_type;
    }
}
