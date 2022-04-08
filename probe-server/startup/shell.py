# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio

from IPython import embed

# for convenient usage
from settings import Setting
from models.redis import *


def main():
    """start an IPython shell to perform some operations"""

    # connect to dbs
    import models
    asyncio.run(models.init_models())

    embed(header='''Probe-Server shell for debugging is now running.''')
