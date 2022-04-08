# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SchedulerHTTPServer",
    "BaseReq"
]

from http_server import *
from settings import Setting


class SchedulerHTTPServer(HTTPServer):
    """scheduler HTTP服务器"""

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "scheduler")

    RELATIVE_IMPORT_TOP_PATH_PREFIX = str(Setting.SETTING_FILE_DIR)
