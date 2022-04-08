#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)
import re
from os import path, system
from pathlib import Path
from subprocess import Popen, PIPE

import click

POM_FILE_DIR: Path = Path(path.dirname(path.dirname(path.realpath(__file__))))


@click.group()
def cli():
    pass


def get_new_version(delta: str) -> str:
    """
    查询当前的pom.xml里记录的版本号，然后根据delta，增加版本号
    :param delta:
    :return:
    """
    version_upgrade_by = [i for i in delta.split(".") if i]
    while 0 <= len(version_upgrade_by) < 3:
        version_upgrade_by.append("-")
    cmd_to_get_version = 'mvn -f "../pom.xml"' \
                         ' org.apache.maven.plugins:maven-help-plugin:3.1.0:evaluate ' \
                         '-Dexpression=project.version -q -DforceStdout'
    try:
        current_version_str = Popen(
            cmd_to_get_version,
            stdout=PIPE,
            shell=True,
            encoding="utf-8").stdout.read()
        current_version = [int(i) for i in current_version_str.split(".")]
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


def judge_if_git_is_clean() -> bool:
    """
    判断当前的git目录是不是都提交了
    :return:
    """
    ret = Popen(
        r'git status',
        stdout=PIPE,
        shell=True,
        encoding="utf-8").stdout.read()
    if_clean = re.compile(r"clean|干净").findall(ret, re.M)
    if not if_clean:
        print("it seems the git repo isn't clean, "
              "commit/stash your changes and try again.")
        return False
    return True


@cli.command("build")
@click.option("--tag",
              type=click.Choice(choices=("dev", "prod"), case_sensitive=True),
              required=True,
              help="image tag")
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
              help="git commit and push after maven package successfully")
@click.option("--commit-msg",
              type=click.STRING,
              required=False,
              default="no msg",
              help="the message for the reversion commit")
def build(tag: str,
          reversion: str,
          push_image: bool,
          push_commit: bool,
          commit_msg: str):
    """build new image with reversion"""

    if not judge_if_git_is_clean():
        return

    # write new version number
    new_version = get_new_version(reversion)
    new_version_slash_separated = new_version.replace(".", "-")
    print(f"version upgraded to {new_version}")
    system(f'mvn -q -f "../pom.xml" versions:set -DoldVersion=* -DnewVersion={new_version} '
           '-DprocessAllModules=true -DallowSnapshots=true -DgenerateBackupPoms=true')

    # make git commit&push
    if push_commit:
        print("gonna git push...")
        system("git add ../pom.xml")
        system(f'git commit -am"reversion to {new_version_slash_separated}：{commit_msg}"')
        system("git push")

    # build docker images and push them if needed
    if not push_image:
        system(f"./dk-build.sh {tag}")
    else:
        system(f"./dk-build.sh {tag} push")


if __name__ == "__main__":
    cli()
