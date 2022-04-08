# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio


def main():
    """(CAUTION)clear all redis db and reset acl&auth"""

    # connect to dbs
    import models
    asyncio.run(models.init_models())

    from models.redis import BaseRedis
    BaseRedis.flush_all()
