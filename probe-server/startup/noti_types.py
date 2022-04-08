# Author: kk.Fang(fkfkbill@gmail.com)

import prettytable


def main():
    """print all noti type-descriptions"""

    from sys_noti.base import SysNotification

    pt = prettytable.PrettyTable(["type", "description"], align="l")
    for c in SysNotification.ALL_SUB_CLASSES:
        pt.add_row((c.TYPE, c.DESCRIPTION))
    print("the following are currently all notification types and descriptions.")
    print(pt)
