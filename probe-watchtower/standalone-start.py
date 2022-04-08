#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)

from os import path, system
from glob import glob
from pathlib import Path


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

for p in glob(str(current_path / "config.json.standalone.d/*.json")):
    bn = path.basename(p)
    print(f"starting container for {bn} ...")
    system(f'''docker run -d \
--name probe-standalone-{bn} \
--restart unless-stopped \
-v {p}:/project/config.json \
-v {str(bound_default_config)}:/project/config.default.json:ro \
--log-opt max-size=5m \
--log-opt max-file=2 \
-e PARAMS="--remark={bn}" \
probe.yamucloud.com:8666/probe/standalone:{docker_image_tag}''')
