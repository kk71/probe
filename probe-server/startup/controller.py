# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio


def main():
    """start a probe controller"""

    loop = asyncio.new_event_loop()

    # connect to dbs
    import models
    asyncio.run(models.init_models())

    # start mqtt client
    from controller.emqx import ControllerEMQXHandler
    loop.create_task(ControllerEMQXHandler.start())

    # start nats client
    from controller.nats import ControllerNATSHandler
    loop.create_task(ControllerNATSHandler.start())

    # register services
    from controller.system_task import SystemTask
    from controller.probe_group import ControllerProbeGroup
    from controller.device import AllDevice
    from controller.http_server import ControllerHTTPServer
    SystemTask.collect()
    ControllerHTTPServer.collect()
    loop.create_task(ControllerProbeGroup.start())
    loop.create_task(AllDevice.sync())
    loop.create_task(AllDevice.force_sync())
    loop.create_task(ControllerHTTPServer.start())

    # start the event loop
    loop.run_forever()
