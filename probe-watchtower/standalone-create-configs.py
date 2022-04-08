#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)

import sys
from os import path
from glob import glob
from pathlib import Path


current_path = Path(path.dirname(path.realpath(__file__)))
try:
    files_to_create = int(sys.argv[1])
except:
    files_to_create = 1
if files_to_create <= 0:
    print(f"illegal nums to create: {files_to_create}")
    exit()

existed_names = [
    path.basename(i)
    for i in glob(str(current_path / "config.json.standalone.d/*.json"))
]

nums_created = 0
i = 0
while len(existed_names) < files_to_create:
    i += 1
    n = f"{i}.json"
    if n not in existed_names:
        with open(str(current_path / "config.json.standalone.d" / n), "w"):
            pass
        existed_names.append(n)
        nums_created += 1
print(f"{nums_created} config file(s) created.")
