Probe Server Docker-Compose
============================

拨测服务端的docker-compose配置，用于管理docker容器模式启动scheduler和controller。


## 配置

### 必要配置

```bash
touch setting.json
touch docker-compose.env
mkdir -p logs/scheduler
mkdir -p logs/controller
```

### 关于镜像

镜像分为separated和standalone两个。

两者区别只是，separated镜像不包含代码，运行的时候代码需要挂载入/project目录，适合线上部署。
standalone镜像包含代码，适合外部部署

如果使用separated模式部署，请将probe-server仓库目录和probe-server-dkc仓库目录置于同一级目录下。

### 关于配置

tag（决定使用哪套服务器的标签）由环境变量TAG决定，使用env文件docker-compose.env配置。该文件并不包含在git的管理范围内

例如：

```ini
TAG=dev
```

tag可用为：dev prod json，当线上时候用，dev和prod分别代表测试服务器和线上服务器。

如果使用standalone镜像，通常需要使用json作为tag，并在setting.json内写入json配置。

### 关于日志

日志文件绑定在logs目录下，scheduler和controller分开，并且各自以日期区分子目录。


## app.sh

这个一个容器内app.py的快捷方式。

```
./app.sh # 具体命令可直接运行，会有提示。
```

注意该命令并不是启动一个容器，而是关联到当前正在运行的(scheduler)容器中去。

## status.sh

通过docker-compose命令查看容器运行状态。

## tail-log.sh

```bash
./tail-log.sh [scheduler|controller|...]
```

用于查看某个实例当日的loguru日志输出，所有日志文件都会按照时间顺序输出在同一个屏幕。

## update-and-down-up.sh

从git仓库更新probe-server当前所在分支的代码，然后清除该目录的全部无用数据（包括__pycache__），然后运行docker-compose down&&docker-compose up -d。

> 注意，仅使用separated镜像有效。
