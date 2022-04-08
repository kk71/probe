# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio

from .nats import *
from .http_server import SeleniumHTTPServer
from utils.schema_utils import *
from utils.sel_utils import *
from utils.log_utils import *
from http_server.handler import BaseReq


analyser_logger = get_bound_logger(__name__)


async def get_corresponding_urls(msg):
    """给出一个url，然后用chrome打开他，获取所有的页面相关的url"""
    params = Schema({
        "url": scm_unempty_str,
        scm_optional("timeout", default=10): scm_gt0_int
    }, ignore_extra_keys=True).validate(msg)
    url = params.pop("url")
    timeout = params.pop("timeout")
    analyser_logger.info(f"start analyse {url=} with {timeout=}...")
    with get_chrome() as b:
        b.get_log("performance")
        b.get(url)
        await asyncio.sleep(timeout)
        logs = b.get_log("performance")
    reqs = get_requests_from_logs(logs)
    analyser_logger.info(f"{url=} analyse done, got {len(reqs)} requests.")
    return {
        "requests": [
            i["request"]["url"] for i in reqs
            # {
            #     "url": i["request"]["url"],
            #     "domain": i["request"]["domain"]
            # } for i in reqs
        ]
    }


@AnalyserNATSHandler.as_callback("chrome_analyser.get_corresponding_urls")
async def nats_get_corresponding_urls(msg):
    return await get_corresponding_urls(msg)


@SeleniumHTTPServer.as_view("corresponding_urls")
class CorrespondingUrlsHandler(BaseReq):

    async def post(self):
        data = await self.get_json_args(scm_any_schema)
        ret = await get_corresponding_urls(data)
        await self.resp(ret)
