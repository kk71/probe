# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "get_mac_address",
    "get_device_type",
    "get_docker_container_id",
    "if_macos",
    "if_root"
]

import os
import re
import uuid
import platform
from subprocess import Popen, PIPE
from typing import Optional

from . import const


def get_mac_address() -> str:
    """获取当前机器网络设备的MAC地址，优先选取当前使用的设备"""
    return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                     for ele in range(0, 8 * 6, 8)][::-1])


def get_device_type() -> int:
    """判断拨测端运行的设备类型"""
    processor: tuple = (platform.processor(), platform.machine())
    return const.DEVICE_TYPE_VM if 'x86_64' in processor or "i386" in processor \
        else const.DEVICE_TYPE_ROUTER


def get_docker_container_id() -> Optional[str]:
    """获取docker容器的id（如果在容器内的话）"""
    ret = Popen(
        r'cat /proc/self/cgroup | head -1',
        stdout=PIPE,
        shell=True,
        encoding="utf-8").stdout.read()
    ids = re.compile(r"/docker/(.*)").findall(ret)
    if len(ids) == 1:
        container_full_id = ids[0]
        print(f"* the probe is running within docker container: {container_full_id}")
        return container_full_id
    print("* seems the probe isn't running within a docker container?")


def if_macos() -> bool:
    """判断当前系统是不是macos"""
    if "macos" in platform.platform().lower():
        return True
    return False


def if_root() -> bool:
    """判断当前类unix系统是否为root"""
    if os.geteuid() != 0:
        return False
    return True


def if_legal_ipv4(s: str) -> bool:
    """
    判断是否为合法的IPv4
    :param s: 不允许前导后续的空格存在
    :return:
    """
    nums = tuple("0123456789.")
    if not isinstance(s, str) or not s.count(".") == 3:
        return False
    for i in s:
        if i not in nums:
            return False
    return True


def get_cpu_info() -> dict:
    """
    查询容器的cpu信息
    :return:
    """
    # TODO 需要注意容器的环境包含lscpu命令
    # 不过一般应该是包含的。
    lscpu_ret = Popen(
        r'lscpu',
        stdout=PIPE,
        shell=True,
        encoding="utf-8").stdout.read()
    try:
        cpus = re.compile(r"^CPU\(s\):\s*(.*)$", re.MULTILINE).findall(lscpu_ret)[0]
        cpus = int(cpus)
    except:
        cpus = 0
    try:
        cpu_mhz = re.compile(r"^CPU MHz:\s*(.*)$", re.MULTILINE).findall(lscpu_ret)[0]
        cpu_mhz = int(cpu_mhz)
    except:
        cpu_mhz = 0
    return {
        "cpus": cpus,
        "cpu_mhz": cpu_mhz
    }
