拨测系统后端
==========

拨测系统的服务端，负责拨测端（在虚拟机、路由器上）的注册，状态管理，拨测任务分发等。

## 发布

使用docker镜像发布，结合probe-server-dkc项目一起部署。

### 版本迭代与打包

进入dockerfiles目录

可通过该命令查看使用方法。需要python3.6+的支持，需要安装python的click包。

bash```
./version-man.py build --help
``

常用方法：

```
./version-man.py build --tag [dev/prod] --commit-msg "press some message"
```

* --tag 指定打包的镜像类型，稳定版/线上环境，请使用prod，测试请使用dev

* --commit-msg 指定提交信息，可简要写一下本次打包的核心要点。

### 仅打包

通常不推荐直接使用该方法发布。

```
./dk-build.sh [prod/dev] [push]
````

* prod/dev表示打包镜像的类型。稳定版/线上环境，请使用prod，测试请使用dev

* push是否推送至harbor仓库。
