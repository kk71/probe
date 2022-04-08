# Author: kk.Fang(fkfkbill@gmail.com)


# 任务的启用禁用状态
ALL_TASK_STATUS = (
    TASK_STATUS_PAUSED := 0,
    TASK_STATUS_ON := 1
)

# target内每个字典的type字段
ALL_TARGET_TYPES = (
    TARGET_TYPE_DOMAIN := "domain",                 # 单个域名
    TARGET_TYPE_DOMAIN_GROUP := "domain_group",     # 域名列表
    TARGET_TYPE_ADDRESS := "address",               # 单个ping地址
    TARGET_TYPE_ADDRESS_GROUP := "addressGroup"     # ping地址组
)

# 默认的拨测端发送主题
PROBE_DEFAULT_RESULT_TOPIC = "results"
