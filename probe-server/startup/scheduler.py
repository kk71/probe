# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio


def main():
    """start a task scheduler"""

    loop = asyncio.new_event_loop()

    # connect to dbs
    import models
    asyncio.run(models.init_models())

    # start mqtt client
    from scheduler.emqx import SchedulerEMQXHandler
    loop.create_task(SchedulerEMQXHandler.start())

    # start nats client
    from scheduler.nats import SchedulerNATSHandler
    loop.create_task(SchedulerNATSHandler.start())

    # register services
    from scheduler.probe_task import ProbeTask
    from scheduler.probe_group import SchedulerProbeGroup
    from scheduler.device import InitializedDevice
    from scheduler.carrier_dns import CarrierDNS
    from scheduler.region import Region
    from scheduler.domain_group import SchedulerCachedDomainGroup
    from scheduler.address_group import SchedulerCachedAddressGroup
    from scheduler.http_server import SchedulerHTTPServer
    ProbeTask.collect()
    SchedulerHTTPServer.collect()
    loop.create_task(ProbeTask.start())
    loop.create_task(SchedulerProbeGroup.start())
    loop.create_task(InitializedDevice.start())
    loop.create_task(Region.start())
    loop.create_task(CarrierDNS.start())
    loop.create_task(ProbeTask.loop_fire())
    loop.create_task(SchedulerCachedDomainGroup.start())
    loop.create_task(SchedulerCachedAddressGroup.start())
    loop.create_task(SchedulerHTTPServer.start())

    # start the event loop
    loop.run_forever()
