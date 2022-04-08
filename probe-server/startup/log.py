# Author: kk.Fang(fkfkbill@gmail.com)

import sys
import asyncio

import click
from loguru import logger

from mq.emqx import *


class EMQXListener(MQTTHandler):

    USER = "viewer"


@click.option("--topics",
              type=click.STRING,
              required=False,
              default="results",
              help="topics to subscribe. use ',' to subscribe more than one topic, "
                   "or ignore this argument to subscribe results topic.")
def main(topics):
    """check the messages from probe in mqtt"""

    def sub(topic):
        @EMQXListener.as_callback(topic)
        async def inner(message, data):
            pass

    if isinstance(topics, str):
        topics = [i.strip() for i in topics.split(",")]

    logger.add(sys.stdout)

    loop = asyncio.get_event_loop()
    loop.create_task(EMQXListener.start())
    for t in topics:
        sub(t)
    loop.run_forever()
