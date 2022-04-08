#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)

import re
from os import system
from subprocess import Popen, PIPE

system("./stop-remove-containers.sh")

print("getting current image ids ...")
ret = Popen(
    r'docker images -a|grep "probe/\|watchtower\|<none>"',
    stdout=PIPE,
    shell=True,
    encoding="utf-8").stdout.read()
image_ids = re.compile(r"^.+?\s+.+?\s+(.+?)\s+", re.M).findall(ret)
if not image_ids:
    print("seems no probe or watcher images???")
    exit()

print(f"gonna remove these images: {image_ids}")
system(rf"docker rmi {' '.join(image_ids)}")

system("./start.sh")
