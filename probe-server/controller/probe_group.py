# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ControllerProbeGroup"
]

from probe_group import *
from .nats import *


class ControllerProbeGroup(ProbeGroup):
    """拨测组"""

    NATS_HANDLER = ControllerNATSHandler
