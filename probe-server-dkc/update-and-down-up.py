#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)

import time
from os import system
from subprocess import Popen, PIPE


def get_image_ids_for_the_dkc():
    ret = Popen(
        r'docker-compose images',
        stdout=PIPE,
        shell=True,
        encoding="utf-8").stdout.read()
    ids = set()
    for i in ret.split("\n")[2:]:
        pre_images_ids = [j for j in i.split(" ") if j]
        if pre_images_ids:
            image_id = pre_images_ids[3]
            ids.add(image_id)
    return ids


print("Updating, down and up the docker-compose...")
ids = get_image_ids_for_the_dkc()
if ids:
    print("stopping and removing old container...")
    system("docker-compose down")
    ids_text = " ".join(ids)
    print(f"old images ids of the containers were: {ids}")
    system(f"docker rmi -f {ids_text}")
system("docker-compose up -d")
time.sleep(3)
system("docker-compose ps")
