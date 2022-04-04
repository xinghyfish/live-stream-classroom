## 0 文档概述

`nginx`的理论知识可以参考《深入理解`Nginx`》（pdf下载链接：[深入理解Nginx模块开发与架构解析](https://github.com/3masterplus/book/blob/master/%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Nginx%E6%A8%A1%E5%9D%97%E5%BC%80%E5%8F%91%E4%B8%8E%E6%9E%B6%E6%9E%84%E8%A7%A3%E6%9E%90.pdf)），本文档主要介绍`linux`平台上`nginx`的安装和编译方法。

---
## 1 环境配置
### 1.1 前言
由于`nginx`在`windows`环境下的性能和兼容性考虑，本项目选择在`linux`平台搭建服务器。
> 实际上，刚开始时头铁在`windows`上搭建服务器，编译和运行过程中碰到许多奇奇怪怪的错误后，果断退坑拥抱 Linus（？）。果然还是原生的好。

在`ubuntu`发行的`linux`版本下，可以通过`apt-get`安装`nginx`，缺点是**无法添加、自定义一些所需要的模块**，因此在本项目中选择手动安装。

### 1.2 编译环境搭建
在一切开始之前，需要安装依赖库以及编译所需要的工具，执行如下命令：
```shell
$ sudo apt install build-essential libpcre3 libpcre3-dev zlib1g-dev unzip git
```
命令执行完成后，基本的编译工具就安装完成了。接下来是模块的安装。

### 1.3 模块组件下载
在下载模块组件时，切记要将各个组件的安装位置放在**同一级目录**下。否则编译指令无法定位到相关文件模块导致编译失败。

#### 1.3.1 `nginx`安装
- 下载地址：http://nginx.org/download/
  - 可下载稳定版
  - `nginx 1.20.1`下载（稳定版）：http://nginx.org/download/nginx-1.20.1.tar.gz
- 也可以通过命令行的形式获取并解压：
```shell
$ curl -O http://nginx.org/download/nginx-1.15.9.tar.gz
$ tar -xvf nginx-1.15.9.tar.gz
```

#### 1.3.2 `OpenSSL`下载（可选）
- 下载地址：https://www.openssl.org/source/
- 命令行下载(以`openssl-1.1.1n`为例)：
```shell
$ curl -O https://www.openssl.org/source/openssl-1.1.1
.tar.gz
$ tar -xvf openssl-1.1.
.tar.gz 
```

#### 1.3.3 `Brotli`下载（可选）
- 命令行下载（不必关注版本）
```shell
$ git clone https://github.com/google/ngx_brotli.git
$ cd ngx_brotli
$ git submodule update --init
$ cd ..
```

### 1.4 编译`nginx`
编译`nginx`时，需要确保上面下载的工具和`nginx`在同一级目录，且命令行参数中**对应版本一致**，否则将会出现错误。如果出现错误，需要仔细查看错误信息，在错误信息中找到错误原因，从而进行定位。
在编译之前，需要确保老版本的`nginx`已被删除干净，删除命令如下：
```shell
$ nginx -V # get arguments
$ sudo systemctl stop nginx
$ sudo apt remove --purge nginx* # remove old version
```
在确保没有旧版本的`nginx`存在后，即可开始编译。以`nginx-1.21.5`为例（实际参数需要根据安装版本设置）：
```shell
$ cd nginx-1.21.5
$ ./configure --user=www-data --group=www-data --add-module=../ngx_brotli --with-openssl=../openssl-1.1.1n  --with-openssl-opt='enable-tls1_3' --with-http_v2_module --with-http_ssl_module --with-http_gzip_static_module --with-http_realip_module
$ make
$ sudo make install
```
如果参数配置正确，则等待编译之后，即可运行`nginx`。

---
## 2 `nginx`启动
编译完成后，系统将自动创建安装和配置文件。`nginx`默认的安装目录为`/usr/local/nginx/`，可执行文件的目录为`/usr/local/nginx/sbin/nginx`，配置文件目录为`/usr/local/nginx/conf/nginx.conf`。
如果需要查找`nginx`安装目录，可以输入如下命令：
```shell
$ whereis nginx
```
可以在终端的输出中获取`nginx`的安装目录。获取安装目录后，启动`nginx`
```shell
$ cd /usr/local/nginx/sbin
$ sudo ./nginx
```
之后，查看`linux`所有开放端口
```shell
$ netstat -ntpl
```
由于默认端口为`80`，因此在本机测试中，`<IP, port>=<0.0.0.0, 80>`即为`nginx`的`socket`，在浏览器中访问`0.0.0.0:80`，如果看到`Welcome to Nginx`字样即为编译成功。

---

## 3 `rtmp-http-flv`编译与配置
### 3.1 `rtmp-hrrp-flv`安装与编译
