# Author: kk.Fang(fkfkbill@gmail.com)

import asyncio

from IPython import embed

# for convenient usage
from settings import Setting


def main():
    """start an IPython shell to perform some operations"""

    embed(header='''Probe shell for debugging is now running.''')
