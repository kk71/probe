# Author: kk.Fang(fkfkbill@gmail.com)

import importlib
from glob import glob
from os import path
from pathlib import Path

import click

CURRENT_DIR = path.dirname(path.realpath(__file__))
CURRENT_PACKAGE = Path(CURRENT_DIR).name


@click.group()
def cli():
    pass


def collect_startup_scripts():
    """
    抓取所有启动脚本
    :return:
    """
    print("Collecting startup scripts ...")
    scripts = glob(str(Path(CURRENT_DIR) / "*.py"))
    for script in scripts:
        _, filename = path.split(script)
        to_import, _ = path.splitext(filename)
        if to_import in ("__init__", "base"):
            continue
        m = importlib.import_module(f"{CURRENT_PACKAGE}.{to_import}")
        cmd = click.decorators._make_command(
            m.main,
            name=to_import.replace("_", "-"),
            cls=click.Command,
            attrs={}
        )
        cmd.__doc__ = m.main.__doc__
        cli.add_command(cmd)
