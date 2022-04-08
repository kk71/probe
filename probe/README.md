Probe - 牙木拨测系统拨测端
=======================

## Installation

Make sure Python 3.8 is installed 

1. Create virtual environment 

```shell script
cd yamuclient
python3.8 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

2. Run the Probe program

```shell script
python probe.py <arguments>
```
```shell
Usage:

--help | -h  Displays this help message.
--server | -s prod/dev  Selects server.
--debug | -d    Turns on debug.
--evil_spawn | -es Turns on evil_spawn
```

If there is no `config.json`, the probe will generate a random uuid as client_id, and create a new config.json. After that all the configurations will be read from that file.

## 路由器拨测端编译方式

……

## 路由器拨测端使用方式

……

## 虚拟机拨测端编译方式

虚拟机拨测端使用docker构建。

```
Dockerfile.dev    # 102测试服务器编译
Dockerfile.prod   # 101线上服务器编译
```

使用如下方法编译一个新的镜像，tag是latest。当前镜像编译完毕后，并不会push到harbor。

```
./dk-build.sh [dev/prod]
```

另有一个脚本可以一个命令编译dev和prod，并且一并推入harbor，但是生产环境请谨慎使用。

实际开发过程中，dev和prod可能不是同一套代码，请务必注意。

```
./dk-build-all-push.sh

# 该脚本运行后需要再一次回车才会继续。
```


### 注意

* 镜像编译需要把本目录的代码一同编译进去，为的是在拨测端使用watchtower拉取到最新的代码。

* 在修改dockerfiles的时候，如无必要，请保证两个dockerfile的内容一致，仅启动容器的命令(CMD)不同。


## 虚拟机拨测端使用方式

请参见probe-watchtower项目
