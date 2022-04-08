#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)

import re
from os import path, system
from pathlib import Path
from subprocess import Popen, PIPE

import click

SETTING_FILE_DIR: Path = Path(path.dirname(path.realpath(__file__)))


@click.group()
def cli():
    pass


def get_new_version(delta: str) -> str:
    version_upgrade_by = [i for i in delta.split(".") if i]
    while 0 <= len(version_upgrade_by) < 3:
        version_upgrade_by.append("-")
    try:
        with open(str(SETTING_FILE_DIR / "VERSION"), "r") as z:
            current_version = [int(i) for i in z.read().split(".")]
            new_version_list = []
            for i in range(3):
                if version_upgrade_by[i] != "-":
                    new_version_list.append(
                        str(current_version[i] + int(version_upgrade_by[i]))
                    )
                else:
                    new_version_list.append("0")
            return ".".join(new_version_list)
    except:
        return "0.0.1"


@cli.command("build")
@click.option("--tag",
              required=True,
              type=click.Choice(("dev", "prod", "standalone"), case_sensitive=True),
              help="target to build")
@click.option("--reversion",
              type=click.STRING,
              required=False,
              default="0.0.1",
              help="the new version delta to upgrade by, e.g. 0.0.2  0.1  1.0.-")
@click.option("--push-image",
              type=click.BOOL,
              required=False,
              default=True,
              help="push images after built")
@click.option("--push-commit",
              type=click.BOOL,
              required=False,
              default=True,
              help="push images after built")
@click.option("--commit-msg",
              type=click.STRING,
              required=False,
              default="no msg",
              help="the message for the reversion commit")
def build(
        tag: str,
        reversion: str,
        push_image: bool,
        push_commit: bool,
        commit_msg: str):
    """build new image with reversion"""

    # first check if the repo is clean
    ret = Popen(
        r'git status',
        stdout=PIPE,
        shell=True,
        encoding="utf-8").stdout.read()
    if_clean = re.compile(r"clean|干净").findall(ret, re.M)
    if not if_clean:
        print("it seems the git repo isn't clean, "
              "commit/stash your changes and try again.")
        return

    # write new version number
    new_version = get_new_version(reversion)
    new_version_slash_separated = new_version.replace(".", "-")
    print(f"version upgraded to {new_version}")
    with open(str(SETTING_FILE_DIR / "VERSION"), "w") as z:
        z.write(new_version)

    # make git commit&push
    if push_commit:
        system("git add ./VERSION")
        system(f'git commit -am"reversion to {new_version_slash_separated}：{commit_msg}"')
        system("git push")

    # build docker images and push them if needed
    if not push_image:
        system(f"./dk-build.sh {tag}")
    else:
        system(f"./dk-build.sh {tag} push")


if __name__ == "__main__":
    cli()
