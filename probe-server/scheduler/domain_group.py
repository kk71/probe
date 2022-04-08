# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SchedulerCachedDomainGroup"
]

from resource_group import *
from .nats import *


class SchedulerCachedDomainGroup(CachedDomainGroup):

    NATS_HANDLER = SchedulerNATSHandler
