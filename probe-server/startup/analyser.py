# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio


def main():
    """start an selenium url analyser with chrome"""

    loop = asyncio.new_event_loop()

    from analyser.nats import AnalyserNATSHandler
    from analyser.http_server import SeleniumHTTPServer
    AnalyserNATSHandler.collect()
    loop.create_task(AnalyserNATSHandler.start())
    loop.create_task(SeleniumHTTPServer.start())

    # start the event loop
    loop.run_forever()
