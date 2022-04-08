# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "get_chrome",
    "get_requests_from_logs"
]

import json
import time
import asyncio
import urllib.parse
from typing import Tuple, Union, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_chrome(
        headless: bool = True,
        window_size: Union[Tuple, List] = (1920, 1080)):
    """
    产生一个selenium的chrome实例
    :param headless: 是否不展示chrome窗体
    :param window_size: chrome窗体理论上的大小
    :return:
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    return webdriver.Chrome(options=chrome_options, desired_capabilities=caps)


def get_requests_from_logs(logs: List[dict],
                           add_domain: bool = True) -> List[dict]:
    """
    查找Network.requestWillBeSent的日志，记录请求的信息
    :param logs:
    :param add_domain: 是否自动加上域名字段
    :return:
    """
    ret = []
    for l in logs:
        try:
            message = json.loads(l["message"])["message"]
            assert message["method"] == "Network.requestWillBeSent"
        except:
            continue
        request_info = message["params"]
        if add_domain:
            url = request_info["request"]["url"]
            parsed_url = urllib.parse.urlparse(url)
            request_info["request"]["domain"] = parsed_url.netloc
        ret.append(request_info)
    return ret


class AsyncWebDriverWait(WebDriverWait):

    async def async_until(self, method, message=''):
        """一个可以用协程睡眠检查代码的until"""
        screen = None
        stacktrace = None

        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._driver)
                if value:
                    return value
            except self._ignored_exceptions as exc:
                screen = getattr(exc, 'screen', None)
                stacktrace = getattr(exc, 'stacktrace', None)
            await asyncio.sleep(self._poll)  # only changed this line
            if time.time() > end_time:
                break
        raise TimeoutException(message, screen, stacktrace)

    async def async_until_not(self, method, message=''):
        """一个可以用协程睡眠检查代码的until_not"""
        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._driver)
                if not value:
                    return value
            except self._ignored_exceptions:
                return True
            await asyncio.sleep(self._poll)  # only changed this line
            if time.time() > end_time:
                break
        raise TimeoutException(message)
