# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio


def main():
    """start statistics and dispatching"""

    loop = asyncio.new_event_loop()

    # connect to dbs
    import models
    asyncio.run(models.init_models())

    # start nats client
    from statistics.nats import StatisticsNATSHandler
    loop.create_task(StatisticsNATSHandler.start())

    # register services
    from statistics.statistics_task import StatisticsTask
    StatisticsTask.collect()
    loop.create_task(StatisticsTask.start())
    loop.create_task(StatisticsTask.loop_fire())

    # start the event loop
    loop.run_forever()
