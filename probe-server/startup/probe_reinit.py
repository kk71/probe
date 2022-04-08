# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio

import aiohttp

from settings import Setting


async def force_init():
    async with aiohttp.ClientSession() as session:
        async with await session.post(f"http://127.0.0.1:{Setting.HTTP_SERVER_PORT}"
                                      f"/controller/device/restful_api/force_reinitialize") as resp:
            print(await resp.json())


def main():
    """force reinitialize all probe devices"""
    asyncio.run(force_init())
