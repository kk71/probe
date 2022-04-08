# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio

import click


@click.option("--remark",
              type=click.STRING,
              required=False,
              default="",
              help="set a default remark only when the remark is empty")
def main(remark):
    """start a probe"""

    loop = asyncio.new_event_loop()

    # 设置拨测端配置的默认备注(仅当拨测端无备注的时候才可以)
    from settings import Setting
    if not Setting.PROBE_COMMENT and remark:
        print(f"* using {remark} as default remark for this probe.")
        Setting.PROBE_COMMENT = remark
    elif Setting.PROBE_COMMENT and remark:
        print(f"this probe already has remark({Setting.PROBE_COMMENT})!")
    else:
        pass

    # start mqtt client
    from probe.emqx import ProbeEMQXHandler
    loop.create_task(ProbeEMQXHandler.start())

    # register services
    from probe.task import Task
    Task.collect()
    loop.create_task(Task.task_cleaner())

    # start the event loop
    loop.run_forever()
