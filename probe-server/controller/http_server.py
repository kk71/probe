# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ControllerHTTPServer",
    "BaseReq"
]

from http_server import *
from settings import Setting


class ControllerHTTPServer(HTTPServer):
    """controller HTTP服务器"""

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "controller")

    RELATIVE_IMPORT_TOP_PATH_PREFIX = str(Setting.SETTING_FILE_DIR)
