Probe-EMQX
===========

拨测系统所用的EMQX服务的docker-compose，包含了配置和自签名证书。

## 配置情况

* 使用redis的db=15作为acl（具体见emqx_auth_redis.conf）

* certs目录下为自签名证书，安全起见，请不要把server开头的证书给客户端。

* 证书的生成方式参考了[https://docs.emqx.net/cloud/latest/cn/deployments/tls_ssl.html](https://docs.emqx.net/cloud/latest/cn/deployments/tls_ssl.html)

* 配置和持久化数据存储在docker volume（probe-emqx-etc, probe-emqx-data），请注意这两个volumes是external，初次docker-compose up -d需要先运行create-volumes.sh以创建它们。docker-compose down不会删除external volumes.

## 注意

>不要使用master分支在dev或者prod上部署。

>不要直接修改dev和prod分支，在master上修改，然后合并到dev和prod上。合并的时候要小心，不要把错误的配置合并到错误的机器上。

### 原因

* 配置(emqx.conf)对应的ssl证书是指向不同域名的。

* 因redis没有集成到docker，acl配置(emqx_auth_redis.conf)对应的redis的IP不同。

## 存在的问题

在dev上测试的时候经常出现emqx.conf和emqx_auth_redis.conf因为文件权限导致容器无法启动的问题，git似乎不能保存文件系统上的文件模式。

使用```change-mod.sh```可以帮你修改这两个文件。

## 关于时区

因为时区问题，emqx官方提供的alpine容器镜像不带有时区功能，需要apt安装时区包。考虑到未来迁移的便携性，还是重新编译自己的镜像比较稳妥。

目前编译的镜像中默认指定了时区为Asia/Shanghai
