#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)

import sys
from os import path, system
from glob import glob
from pathlib import Path


# get which probe with config number to re-create
try:
    probe_setting_file_name = int(sys.argv[1])
except IndexError:
    probe_setting_file_name = int(input("enter the config number: "))
print(f"going to re-create the container for {probe_setting_file_name}.json ...")


current_path = Path(path.dirname(path.realpath(__file__)))
with open(current_path / "standalone-image-tag", "r") as z:
    docker_image_tag: str = z.read().strip()
if not docker_image_tag:
    docker_image_tag = "latest"
print(f"using probe tag: {docker_image_tag}")


bound_default_config = current_path / "config.default.json"
if not path.exists(str(bound_default_config)):
    print("make sure config.default.json is present")
    exit()
if path.isdir(str(bound_default_config)):
    print("config.default.json should be a json file, not directory.")
    exit()


for p in glob(str(current_path / f"config.json.standalone.d/{probe_setting_file_name}.json")):
    bn = path.basename(p)
    container_name = f"probe-standalone-{bn}"
    print(f"stopping and remove container for {bn} if necessary ...")
    system(f"docker stop {container_name}")
    system(f"docker rm {container_name}")
    print(f"starting container for {bn} with cpu and memory options ...")
    exec_cmd = input("using another container startup execution command? "
                     "leave empty to skip and use the default: ")
    exec_cmd = exec_cmd.strip()
    system(f'''docker run -d \
--name {container_name} \
--restart unless-stopped \
--cpuset-cpus="1" \
--memory=1024M --memory-swap=1024M \
-v {p}:/project/config.json \
-v {str(bound_default_config)}:/project/config.default.json:ro \
--log-opt max-size=5m \
--log-opt max-file=2 \
-e PARAMS="--remark={bn}" \
probe.yamucloud.com:8666/probe/standalone:{docker_image_tag} {exec_cmd}''')
    system(f"""docker logs -f {container_name}""")
