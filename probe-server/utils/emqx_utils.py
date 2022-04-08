# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "EMQXHttpAPI"
]

import json

import aiohttp

from settings import Setting


class EMQXHttpAPI:
    """EMQX的HTTP API"""

    session = None

    EMQ_API_URL = f"http://{Setting.EMQ_HTTP_USERNAME}:{Setting.EMQ_HTTP_PASSWORD}@" \
                  f"{Setting.EMQ_HOST}:{Setting.EMQ_HTTP_PORT}/api/v4/"

    @classmethod
    def get_session(cls):
        if not cls.session:
            cls.session = aiohttp.ClientSession()
        return cls.session

    @staticmethod
    def http_code_info(code: int) -> str:
        """ Takes in the http response code and outputs human readable information"""
        http_response_dict = {
            200: "Succeed, and the returned JSON data will provide more information",
            400: "Invalid client request, such as wrong request body or parameters",
            401: "Client authentication failed , maybe because of invalid authentication credentials",
            404: "The requested path cannot be found or the requested object does not exist",
            500: "An internal error occurred while the server was processing the request"
        }

        return http_response_dict[code]

    @staticmethod
    def response_code_info(code: int) -> str:
        """ Takes in the json response and shows the emqx response info """
        response_dict = {
            0: "Succeed",
            101: "RPC error",
            102: "unknown mistake",
            103: "wrong user name or password",
            104: "Empty username or password",
            105: "User does not exist",
            106: "Administrator account cannot be deleted",
            107: "Missing key request parameters",
            108: "Request parameter error",
            109: "Request parameters are not in legal JSON format",
            110: "Plug-in is enabled",
            111: "Plugin is closed",
            112: "Client is offline",
            113: "User already exists",
            114: "Old password is wrong",
            115: "Illegal subject"
        }
        return response_dict[code]

    @classmethod
    async def publish_topic(cls, topic: str, payload: dict):
        """
        Publish a message to EMQX server
        :param topic:
        :param payload:
        :return:
        """
        post_data = {
            "clientid": Setting.EMQ_USERS["controller"]["client_id"],
            "payload": json.dumps(payload),
            "topic": topic
        }
        await cls.get_session().post(cls.EMQ_API_URL + 'mqtt/publish', json=post_data)

    @classmethod
    async def get_client_info(cls, client_id: str):
        r = await cls.get_session().get(cls.EMQ_API_URL + f'clients/{client_id}')
        response_json = await r.json()
        return response_json['data']

    @classmethod
    async def get_all_clients(cls, page_limit=10000):
        """
        返回集群下所有客户端的信息，支持分页。
        """
        data = []
        page = 1
        while True:
            r = await cls.get_session().get(
                cls.EMQ_API_URL + 'clients',
                params={"_page": page, "_limit": page_limit}
            )
            resp = await r.json()
            data.extend(resp["data"])
            page += 1
            if resp["meta"]["count"] <= len(data):
                break
        return data

    @classmethod
    async def subscribe_to_topics(cls, client_id, topics: [str]):
        params = {
            "clientid": client_id,
            "topics": ','.join(topics),
            "qos": 1
        }
        r = await cls.get_session().post(cls.EMQ_API_URL + "mqtt/subscribe", json=params)
        return (await r.json())['code'] == 0
