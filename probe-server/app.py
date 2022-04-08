#!/usr/bin/env python3
# Author: kk.Fang(fkfkbill@gmail.com)

print(f"YAMU Probing System server-side is starting ...")

# initialize setting
import settings
the_tag = settings.BaseSetting.from_env("TAG", None)
if not the_tag:
    try:
        with open(str(settings.BaseSetting.SETTING_FILE_DIR / "TAG"), "r") as z:
            the_tag = z.read().strip()
            if not the_tag:
                raise Exception("* no TAG environment variable is set, "
                                "and the TAG file seems to be empty.")
    except FileNotFoundError:
        raise Exception("* neither TAG environment variable is set "
                        "nor the TAG file is present.")
settings.BaseSetting.set_current_setting(the_tag)

# startup
from startup import *
collect_startup_scripts()
cli()
