# Author: kk.Fang(fkfkbill@gmail.com)

import time
import asyncio
from typing import List, AnyStr

import click
import icmplib.ping
from dns.asyncresolver import Resolver


@click.option("--target",
              type=click.Choice(["dns", "dns_s", "ping", "ping_s"]),
              required=True,
              help="which target to test")
@click.option("--seconds",
              type=click.FLOAT,
              required=False,
              default=1,
              help="seconds to run the stress test")
@click.option("--tasks",
              type=click.INT,
              required=False,
              default=500,
              help="task to run the stress test")
def main(target: str, seconds: float, tasks: int):
    """stress tests"""
    r = ""
    if target == "dns_s":
        r = asyncio.run(test_dns_s(seconds))
    elif target == "dns":
        r = asyncio.run(test_dns(tasks))
    elif target == "ping_s":
        r = asyncio.run(test_ping_s(seconds))
    elif target == "ping":
        r = asyncio.run(test_ping(tasks))
    else:
        assert 0
    time.sleep(3)
    print(r)


async def test_ping_s(time_to_send):
    dest = "180.101.49.12"  # www.baidu.com

    t1 = time.time()
    tasks = []
    while not time.time() - t1 >= time_to_send:
        tasks.append(asyncio.create_task(icmplib.async_ping(dest, count=1, timeout=3)))
    try:
        await asyncio.wait(tasks)
    except:
        pass
    t2 = time.time()
    all_done_time_cost = round(t2 - t1, 3)
    return f"test for ping in {time_to_send}s, " \
           f"send {len(tasks)} asynchronously, " \
           f"all done in {all_done_time_cost}s, " \
           f"all done on average {round(len(tasks) / all_done_time_cost, 3)}/s"


async def test_dns_s(time_to_send):
    dest = "www.baidu.com"
    dns_nameservers: List[AnyStr] = ["114.114.114.114"]

    t1 = time.time()
    tasks = []
    while not time.time() - t1 >= time_to_send:
        resolver = Resolver(configure=False)
        resolver.lifetime = 2.0
        resolver.nameservers = dns_nameservers
        tasks.append(asyncio.create_task(resolver.resolve(dest, rdtype="A", tcp=False, raise_on_no_answer=False)))
    try:
        await asyncio.wait(tasks)
    except:
        pass
    t2 = time.time()
    all_done_time_cost = round(t2 - t1, 3)
    return f"test for dns in {time_to_send}s, " \
           f"send {len(tasks)} asynchronously, " \
           f"all done in {round(t2 - t1, 3)}s, " \
           f"all done on average {round(len(tasks) / all_done_time_cost, 3)}/s"


async def test_ping(tasks_num: int):
    dest = "180.101.49.12"  # www.baidu.com

    tasks = []
    t1 = time.time()
    for i in range(tasks_num):
        tasks.append(asyncio.create_task(icmplib.async_ping(dest, count=1, timeout=3)))
    t2 = time.time()
    await asyncio.wait(tasks)
    t3 = time.time()
    all_done_time_cost = round(t3 - t1, 3)
    return f"test for ping with {tasks_num} requests, " \
           f"send in {round(t2 - t1, 3)}s asynchronously, " \
           f"all done in {all_done_time_cost}s, " \
           f"all done average {round(tasks_num / all_done_time_cost, 3)}/s"


async def test_dns(tasks_num: int):
    dest = "www.baidu.com"
    dns_nameservers: List[AnyStr] = ["114.114.114.114"]

    tasks = []
    t1 = time.time()
    for i in range(tasks_num):
        resolver = Resolver(configure=False)
        resolver.lifetime = 2.0
        resolver.nameservers = dns_nameservers
        tasks.append(asyncio.create_task(resolver.resolve(dest, rdtype="A", tcp=False, raise_on_no_answer=False)))
    t2 = time.time()
    await asyncio.wait(tasks)
    t3 = time.time()
    all_done_time_cost = round(t3 - t1, 3)
    return f"test for dns with {tasks_num} requests, " \
           f"send in {round(t2 - t1, 3)}s asynchronously, " \
           f"all done in {all_done_time_cost}s, " \
           f"all done average {round(tasks_num / all_done_time_cost, 3)}/s"
