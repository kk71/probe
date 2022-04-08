# Author: kk.Fang(fkfkbill@gmail.com)


__all__ = [
    "SeleniumHTTPServer",
    "BaseReq"
]

from http_server import *
from settings import Setting


class SeleniumHTTPServer(HTTPServer):
    """selenium HTTP服务器"""

    PATH_TO_IMPORT = str(Setting.SETTING_FILE_DIR / "analyser")

    RELATIVE_IMPORT_TOP_PATH_PREFIX = str(Setting.SETTING_FILE_DIR)
