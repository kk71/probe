# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SchedulerProbeGroup"
]

from probe_group import *
from .nats import *


class SchedulerProbeGroup(ProbeGroup):
    """拨测组"""

    NATS_HANDLER = SchedulerNATSHandler
