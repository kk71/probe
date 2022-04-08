# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "AnalyserNATSHandler"
]

from mq.nats import *
from settings import Setting


class AnalyserNATSHandler(NATSHandler):
    """监听nats"""

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "analyser")

    RELATIVE_IMPORT_TOP_PATH_PREFIX = str(Setting.SETTING_FILE_DIR)
