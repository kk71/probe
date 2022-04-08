# Author: kk.Fang(fkfkbill@gmail.com)


class BaseMQException(Exception):
    """基础消息队列通用异常"""
    pass


class MQTimeoutException(BaseMQException):
    """消息队列返回超时"""
    pass
