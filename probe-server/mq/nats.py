# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "NATSHandler",
    "NATSRequestHandler"
]

import uuid
import json
import asyncio
import traceback
from typing import Type

from nats.aio.client import Client

from utils.schema_utils import *
from core.message_queue_handler import *
from settings import Setting
from utils.dt_utils import *
from logger import *


class NATSHandler(
        MessageQueueHandler, metaclass=SCCLoggerMixin):
    CONNECTOR: Client = None

    CALLBACKS = []

    @classmethod
    async def start(cls, *args, **kwargs):
        cls.CONNECTOR = Client()
        await cls.CONNECTOR.connect(
            servers=[f"nats://{Setting.NATS_IP}:{Setting.NATS_PORT}"],
            user=Setting.NATS_USER,
            password=Setting.NATS_PASSWORD,
            error_cb=cls.on_error,
            closed_cb=cls.on_closed,
            disconnected_cb=cls.on_disconnected,
            reconnected_cb=cls.on_reconnected,
        )
        await cls.process_subscribe()

    @classmethod
    async def process_subscribe(cls):
        for args, kwargs, a_callable in cls.CALLBACKS:
            await cls.CONNECTOR.subscribe(args[0], cb=a_callable)
            cls.logger.info(f"{cls}: {args[0]}")

    @classmethod
    async def on_error(cls, e):
        cls.logger.error(traceback.format_exc())
        cls.logger.error(e)
        cls.logger.error(f"NATS client {cls} raises errors.")

    @classmethod
    async def on_closed(cls):
        cls.logger.error(f"NATS client {cls} is closed.")

    @classmethod
    async def on_disconnected(cls):
        cls.logger.error(f"NATS client {cls} is disconnected.")

    @classmethod
    async def on_reconnected(cls):
        cls.logger.info(f"NATS client {cls} is reconnected.")
        await cls.process_subscribe()

    @classmethod
    async def serialize(cls, obj, convert_dt_to_str: bool = True, **kwargs):
        if convert_dt_to_str:
            obj = dt_to_str(obj)
        return super().serialize(obj, **kwargs).encode("utf-8")

    @classmethod
    def gen_decorated_cb(cls, args, kwargs, a_callable):
        async def callback_preprocess(msg):
            d = json.loads(msg.data.decode())
            if kwargs.get("log", Setting.NATS_CALLBACK_LOG):
                cls.logger.debug(
                    f"{cls.__name__}[IN] - subject: {msg.subject}, reply: {msg.reply}, data: {d}")
            ret = await a_callable(d)
            if msg.reply:
                await cls.publish(msg.reply, ret, t="REPLY")  # response

        return callback_preprocess

    @classmethod
    def _msg_out(cls, subject: str, payload, t="OUT"):
        """
        提示有消息发送出去
        :param subject:
        :param payload:
        :param t: 指定发出去的消息是什么目的，默认OUT泛指一切发出去消息
        :return:
        """
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        cls.logger.debug(f"{cls.__name__}[{t}] - subject: {subject}, data: {payload}")

    @classmethod
    async def publish(cls, subject: str, payload, **kwargs):
        serialized_payload = await cls.serialize(payload)
        cls._msg_out(subject, serialized_payload, **kwargs)
        return await cls.CONNECTOR.publish(subject, serialized_payload)

    @classmethod
    async def request(cls,
                      nats_request_handler: Type["NATSRequestHandler"],
                      **kwargs):
        """
        执行request，处理返回，以及返回的超时处理。
        TODO 如果不要返回结果不处理超时，请使用request_no_cb
        :param nats_request_handler:
        :param kwargs: 即request()的输出参数
        :return:
        """
        expected = 1  # the messages expected returned from reply subject
        subject = nats_request_handler.SUBJECT
        if callable(subject):
            subject = subject()
        reply_subject = nats_request_handler.REPLY_SUBJECT
        if callable(reply_subject):
            reply_subject = reply_subject()
        payload = await cls.serialize(
            obj=await nats_request_handler.request(**kwargs),
            **kwargs
        )
        future = asyncio.Future(loop=cls.CONNECTOR._loop)
        sid = await cls.CONNECTOR.subscribe(
            reply_subject,
            future=future,
            max_msgs=expected
        )
        await cls.CONNECTOR.auto_unsubscribe(sid, 1)
        cls._msg_out(subject, payload, t="REQUEST")
        await cls.CONNECTOR.publish_request(subject, reply_subject, payload)
        try:
            msg = await asyncio.wait_for(
                future,
                nats_request_handler.TIMEOUT,
                loop=cls.CONNECTOR._loop
            )
            try:
                return await nats_request_handler.response_cb(msg=msg)
            except NotImplementedError:
                pass  # 表示不需要等待回复
        except asyncio.TimeoutError:
            await cls.CONNECTOR.unsubscribe(sid)
            future.cancel()
            cls.logger.error(f"NATS request timeout: {nats_request_handler}: {kwargs}")
            try:
                return await nats_request_handler.timeout()
            except NotImplementedError:
                pass  # 表示不需要等待回复

    @classmethod
    async def request_no_cb(cls,
                            nats_request_handler: Type["NATSRequestHandler"],
                            **kwargs):
        """
        执行request，不监听返回，不处理超时
        :param nats_request_handler:
        :param kwargs: 即request()的输出参数
        :return:
        """
        subject = nats_request_handler.SUBJECT
        if callable(subject):
            subject = subject()
        payload = await nats_request_handler.request(**kwargs)
        return await cls.publish(subject, payload)


class NATSRequestHandler(
        MessageQueueRequestHandler, metaclass=SCCLoggerMixin):
    """适用于nats的请求/返回"""

    # 收集全部适用于nats的请求
    # TODO 不要再在子类里重新初始化了
    ALL_SUB_CLASSES = []

    # 定义请求的subject
    SUBJECT = None  # required

    TIMEOUT = 3

    @classmethod
    def _reply_subject(cls):
        s = f"{cls.SUBJECT}:{uuid.uuid4().hex}"
        # cls.logger.debug(f"using reply subject: {s}")
        return s

    # 定义返回的subject
    REPLY_SUBJECT = _reply_subject
    del _reply_subject

    @classmethod
    async def request(cls, **kwargs):
        return

    @classmethod
    async def response_cb(cls, msg, **kwargs):
        d = json.loads(msg.data.decode("utf-8"))
        return cls.response_schema().validate(d)

    @classmethod
    def response_schema(cls):
        return Schema(object)
