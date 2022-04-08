# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "MQTTHandler"
]

import json
import asyncio
from contextlib import AsyncExitStack
from typing import Union, Callable

from asyncio_mqtt.client import Client

from settings import Setting
from core.message_queue_handler import *
from logger import *
from utils.dt_utils import *
from utils.decorators import func_loop


class MQTTHandler(MessageQueueHandler, metaclass=SCCLoggerMixin):

    CONNECTOR: Client = None

    CONNECTED: bool = False

    # USER即setting.py中EMQ_USERS的key
    # 注意：参数client_id接受callable对象，无输入运行输出即client_id
    USER: str = None

    CALLBACKS = []

    @staticmethod
    async def _watcher(messages_iterator, a_callable):
        async for msg in messages_iterator:
            await a_callable(msg)

    @staticmethod
    async def _cancel_tasks(tasks):
        for task in tasks:
            if task.done():
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    @staticmethod
    async def log_messages(messages):
        async for message in messages:
            pass  # do nothing

    @classmethod
    async def _start(cls, connector: Client):
        async with AsyncExitStack() as stack:
            tasks = set()
            stack.push_async_callback(cls._cancel_tasks, tasks)
            await stack.enter_async_context(connector)
            for args, _, a_callable in cls.CALLBACKS:
                a_topic: str = args[0]
                await connector.subscribe(a_topic)
                manager = connector.filtered_messages(a_topic)
                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(cls._watcher(messages, a_callable))
                tasks.add(task)
                cls.logger.info(f"{cls}: {args[0]}")
            if not tasks:
                # 如果没有监听任何频道，mqtt连接就退出了。
                # 这个时候需要创建一个空任务
                # Messages that doesn't match a filter will get logged here
                messages = await stack.enter_async_context(connector.unfiltered_messages())
                task = asyncio.create_task(cls.log_messages(messages))
                tasks.add(task)

            cls.logger.info(f"mqtt client {cls} is connected")
            cls.CONNECTED = True
            await cls.on_connected()
            await asyncio.gather(*tasks)

    @classmethod
    def _connector(cls):
        client_id = Setting.EMQ_USERS[cls.USER]["client_id"]
        # 注意：参数client_id接受callable对象，无输入运行输出即client_id
        if callable(client_id):
            client_id = client_id()
        connector = Client(
            Setting.EMQ_DOMAIN,
            Setting.EMQ_SERVICE_PORT,
            username=Setting.EMQ_USERS[cls.USER]["username"],
            password=Setting.EMQ_USERS[cls.USER]["password"],
            client_id=client_id
        )
        if Setting.EMQ_USE_SSL:
            cls.logger.info("connecting to MQTT server through SSL ...")
            connector._client.tls_set(
                ca_certs=str(Setting.SETTING_FILE_DIR / "certs" / Setting.EMQ_DOMAIN / "root-ca.crt"),
                certfile=str(Setting.SETTING_FILE_DIR / "certs" / Setting.EMQ_DOMAIN / "client.crt"),
                keyfile=str(Setting.SETTING_FILE_DIR / "certs" / Setting.EMQ_DOMAIN / "client.key")
            )
        return connector

    @classmethod
    @func_loop
    async def start(cls, *args, **kwargs):
        cls.CONNECTED = False
        cls.CONNECTOR = cls._connector()
        async with cls.CONNECTOR:
            await cls._start(cls.CONNECTOR)

    @classmethod
    async def on_connected(cls):
        """mqtt连接建立好，频道订阅结束之后的回调"""
        pass

    @classmethod
    def gen_decorated_cb(cls, args, kwargs, a_callable):
        async def callback_preprocess(message):
            if kwargs.get("log", Setting.EMQ_CALLBACK_LOG):
                to_print = message.payload
                if isinstance(to_print, bytes):
                    try:
                        to_print = to_print.decode("utf-8")
                    except:
                        pass
                cls.logger.debug(f"{cls.__name__}[IN] - topic: {message.topic}, data: {to_print}")
            try:
                d = json.loads(message.payload)
            except json.JSONDecodeError:
                d = message.payload
            return await a_callable(message, d)

        return callback_preprocess

    @classmethod
    async def publish(cls, topic, payload=None, **kwargs):
        kwargs.update({"topic": topic, "payload": payload})
        if "qos" not in kwargs.keys():
            kwargs["qos"] = 2
        cls.logger.debug(f"{cls.__name__}[OUT] - topic: {topic}, data: {payload}")
        return await cls.CONNECTOR.publish(**kwargs)

    @classmethod
    async def publish_json(
            cls,
            topic: str,
            payload: Union[dict, list] = None,
            convert_dt_to_str: bool = True,
            **kwargs):
        if convert_dt_to_str:
            payload = dt_to_str(payload)
        # 判断一下设置，是否需要对输出的json文本进行缩进美化
        indentation = 4
        if Setting.EMQ_PUBLISH_JSON_SIMPLIFY:
            indentation = None
        payload = json.dumps(payload, ensure_ascii=False, indent=indentation)
        return await cls.publish(topic, payload, **kwargs)

    @classmethod
    async def temp_subscription_with_cb(cls,
                                        topic: str,
                                        cb: Callable,
                                        ttl: int = 5):
        """
        带超时时间的临时订阅
        这个"超时"其实不是真的超时，而是等待时间。因为mqtt的消息能返回多少，其实是不确定的
        只能用时间阈值去拦截，在规定时间内的即命中，超过时间的即舍弃。
        :param topic: 订阅的临时主题
        :param cb: 回调，必须是协程函数，仅接受一个可迭代的参数
        :param ttl: 等待时间，秒
        :return:
        """
        assert isinstance(topic, str)
        assert callable(cb)

        await cls.CONNECTOR.subscribe(topic, qos=2)

        async def _cb():
            async with cls.CONNECTOR.filtered_messages(topic) as messages_iterator:
                await cb(messages_iterator)

        the_task = asyncio.create_task(_cb())
        await asyncio.sleep(ttl)
        await cls.CONNECTOR.unsubscribe(topic, timeout=3)
        if not the_task.cancelled() and not the_task.done():
            try:
                the_task.cancel()
            except:
                pass  # no need to do anything
        cls.logger.info(f"{cls}: temporary topic subscription '{topic}' is done")
