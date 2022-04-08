# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SchedulerCachedAddressGroup"
]

from resource_group import *
from .nats import *


class SchedulerCachedAddressGroup(CachedAddressGroup):

    NATS_HANDLER = SchedulerNATSHandler
