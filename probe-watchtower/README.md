虚拟机拨测端部署配置
================

用于部署虚拟机拨测端的一些配置和安装脚本。

## 系统要求

CentOS7，需要安装至少python3.8+

## 安装包

http://dev.probe.yamucloud.com:5678/probe-watchtower.tar.gz

解压后的目录作为拨测点的安装目录。如果需要备份拨测点，请直接备份该目录。

## 安装配置docker

```bash
./install.sh
```

运行结束之后，请关注hello-world镜像是否顺利运行且退出了。

docker安装结束后，可以配置安装拨测端。拨测端分为两种部署模式。

## 牙木云公网线上部署模式

使用运行在牙木服务器（probe.yamucloud.com）上的线上公网拨测服务作为服务端，安装拨测点。

特点：拨测镜像使用watchtower自动更新，可同时部署prod和dev两套拨测点，不需要手动修改拨测服务器配置。

拨测端部署后，可[前往配置](http://probe.yamucloud.com:15601/)

请注意，公网部署时，一个操作系统只能部署一套拨测点。

### 启动

```bash
./start.sh
```

### 附加工具

正常运行不需要使用附加工具，仅作调试用。

#### force-restart.py

此脚本会尝试停止并删除probe-prod, probe-dev, watchtower三个容器，并且删掉它们的镜像，然后重新运行start.sh

> 注意：需要python3.8+支持

#### status.sh

查看拨测端相关的容器运行状态。

#### tail-log.sh

查看dev或者prod的docker日志，使用方式：

```
./tail-log.sh [dev/prod]
```

请注意，容器在起来的时候已经配置好了日志上限，具体请看start.sh


## 线下/单点/独立拨测服务部署模式

> 注意：需要python3.8+支持

为独立部署的拨测系统提供拨测端，场景：线下安装，内网部署，单点部署等等。

特点：不需要与牙木云互通，手动升级拨测端，可能无公网访问，单点部署，单点多拨测端部署等等。

### 配置

请先修改缺省配置，```config.default.json```

```bash
echo '''{
    "EMQ_DOMAIN": "填入拨测系统的IP"
}''' > config.default.json

```

### 启动

启动原理：脚本根据```config.json.standalone.d```目录下的配置文件个数，对应启动一个拨测端容器。
容器的配置即写入对应的文件。

初次使用，需要手动创建空配置文件。

以下脚本不带任何参数，默认只创建一个配置文件。大部分场景单机单个拨测端即可满足需求。

```bash
./standalone-create-configs.py

```

如果要多个拨测端，在后面带上个数。如果需要在单机启动多个拨测端，请使用这个方法。

```bash
./standalone-create-configs.py [num]

```

脚本会自动检测```config.json.standalone.d```目录里有几个配置文件，如果存在足够配置文件，就不会新增，否则会增加到足够个数。

使用如下命令启动：

```bash
./standalone-start.py

```

### 附加工具

正常运行不需要使用附加工具，仅作调试用。

#### standalone-force-restart.py

此脚本会尝试停止并删除probe-standalone*容器，并且删掉镜像，然后重新运行standalone-start.py

> 注意：需要python3.8+支持

#### standalone-status.sh

查看拨测端相关的容器运行状态。
