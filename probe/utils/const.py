# Author: kk.Fang(fkfkbill@gmail.com)


# 时间格式(arrow)

COMMON_DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'
COMMON_DATE_FORMAT = 'YYYY-MM-DD'
COMMON_DATE_FORMAT_COMPACT = 'YYYYMMDD'
COMMON_TIME_FORMAT = 'HH:mm:ss'


# 设备管理操作行为
ALL_DEVICE_MANAGEMENT_ACTIONS = (
    DEVICE_MANAGEMENT_ACTION_REGISTER := "register"    # 申请注册
)

# 临时消息频道
EMQX_TEMP_TOPIC_PREFIX = "temp_topic/"

# 所有拨测端可运行的设备类型
ALL_DEVICE_TYPES = (
    DEVICE_TYPE_VM := 0,
    DEVICE_TYPE_ROUTER := 1
)
