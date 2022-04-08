# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "HTTPServer"
]

import asyncio
from pathlib import Path

import prettytable
from tornado.web import StaticFileHandler, Application

from core.self_collecting_class import *
from settings import Setting
from .handler import *
from logger import *


class HTTPServer(SelfCollectingFramework, metaclass=SCCLoggerMixin):
    """一个通用的http服务器"""

    URL_ROOT_PREFIX: str = "/"

    HANDLERS = [
        # static prefix
        (
            str(Setting.SETTING_FILE_DIR / "(.*)"),
            StaticFileHandler,
            {"path": Setting.STATIC_DIR}
        )
    ]

    @classmethod
    async def start(cls):
        if Setting.HTTP_SERVER_ENABLED:
            app = Application(cls.HANDLERS)
            a_server = app.listen(Setting.HTTP_SERVER_PORT, Setting.HTTP_SERVER_IP)
            await asyncio.sleep(5)
            return a_server

    @classmethod
    def as_view(cls, route_rule: str = ""):
        """
        请求装饰器
        :param route_rule: 相对的url路径，缺省以模块名作为路径
        :return:
        """
        if route_rule:
            assert route_rule.strip()[0] != "/"

        def as_view_inner(req_handler: BaseReq):
            split_path = [
                i
                for i in req_handler.__module__.split(".")
                if i.lower() not in ("", "__init__")
            ]
            route = cls.URL_ROOT_PREFIX / Path("/".join(split_path)) / route_rule
            cls.HANDLERS.append((str(route), req_handler))
            return req_handler

        return as_view_inner
