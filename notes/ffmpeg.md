# FFmpeg：基础知识

## 媒体文件

媒体文件的抽象组成：容器 ( *container* ) + 流 ( *stream* )

- **容器**：将流封装起来，对外提供流的唯一**接口**
- **流**：包含AV组件（语音+视频），使用编码方法对其进行编码

因此，选择合适的格式和容器来存储媒体文件就非常重要。FFmpeg 能够自动选择合适的格式和容器，而不需要进行复杂的配置。

## 基本转换

在命令行中使用`ffmpeg`处理音频文件的基本格式如下：

```shell
ffmpeg -i input.mp3 output.ogg
```

使用`ffmpeg`命令，其中`input.mp3`表示输入文件，`output.ogg`表示转化为Vorbis语音流并封装在OGG容器中。对于视频文件的处理也有类似的命令：

```shell
ffmpeg -i input.mp4 output.webm
```

# 网络直播：RTMP和推流技术

## 推流概述

推流的概念如下：

> 推流，指的是把**采集阶段封包好的内容传输到服务器**的过程。其实就是将现场的视频信号传到网络的过程。

在实际中，推流的工作流如下：

1. 由【推流端】采用**上行RTMP**推流到【源站】
2. 【源站】通过**RTMP拉流**到【CDN分发节点】
3. 【CDN分发节点】通过不同的拉流协议拉流到不同的【播放端】

值得注意的是，上述整个工作流程传输的音视频数据都是压缩的数据流，解码的工作在播放段进行解码，这也是不同播放端采取不同拉流协议的原因。

## RTMP协议

`RTMP`的全称为`Real Time Messaging Protocol`，即**实时消息传输协议**，在计算机网络中处于**应用层**。`RTMP`一般在TCP层传输`flv`格式流，该格式即属于上文提到的容器，作为数据流的封装。

> `flv`格式全称为`flash video`，是Adobe公司开发的一种网络视频格式，详细参考词条：[Flash Video - 维基百科，自由的百科全书 (wikipedia.org)](https://zh.wikipedia.org/wiki/Flash_Video)。

RTMP协议族使用的默认端口为1935，除了基本协议外还包括多个变种，每个变种都支持不同的功能，例如加密、使用UDP作为传输层等。更多细节这里不做过多赘述，在参考内容中可以进一步学习。

## 使用ffmpeg的rtmp推流

使用`ffmpeg`协议进行最基础的rtmp推流的命令行的格式如下：

```shell
ffmpeg -i ${input_video} -f flv rtmp://${server}/live/${streamName}
```

- `-i`：`input`，表示输入视频文件，后跟`${input_video}$`表示视频文件路径/URL。
- `-f`：`format`，强制ffmpeg采用某种格式，后跟对应的格式。

# 推流直播demo设计

## 直播流程

### 逻辑流程

1. 调用摄像头获取音频和图像
2. 将视频分割为帧
3. 将每一帧进行需求加工后，将此帧写入pipe管道
4. 利用`ffmpeg`进行推流直播

环境配置：`nginx`服务器 + `nginx-rtmp-module` + `ffmpeg`

### 技术实现

- 【视频采集端】：视频输入的数据采集设备
- 【直播流视频服务端】：一台`Nginx`服务器，采集视频录制端传输的视频流(`H264/ACC`编码)，由服务器端进行解析编码，推送`RTMP/HLS`格式视频流至视频播放端。
- 【视频播放端】：视频输出端设备相关软件，本项目计划采用`HTML5`的`video`标签

因此，需要针对上述技术进行实现。

## 推拉流测试(Windows端)

在对`nginx`进行配置的过程中遇到了一些困难，在实际进行推流、拉流测试的过程中遇到了非常多的错误（`Unknown error`，`I/O error`等各种类型的错误），最后按照参考内容5介绍的方法成功实现了的推流拉流的测试。下面是一些配置和指令：

- 推流地址：`rtmp://127.0.0.1:1935/live/home`
- 推流测试：`ffmpeg.exe -re -i ${input-file-path} -vcodec libx264 -acodec aac -f flv rtmp://127.0.0.1:1935/live/home`
- 拉流测试：`ffplay.exe rtmp://localhost:1935/live/home`

按照上面的指令，终于完成了推拉流`mp4`文件的简单测试。初步猜测可能是文件路径中`\`写为`/`或路径没有均采取小写导致的。实际测试时，推流的文件地址为：`D:\server\videos\test.mp4`，但是测试时正确的路径为`d:\server\videos\test.mp4`，终于完成测试。明天预计实现摄像头和麦克风等硬件设备的推流测试。计划项目后期将`nginx.conf`配置文件的相关内容进行更为深入的探究。

### 硬件设备数据推流

在直播时，我们主要需要的**功能**为：共享屏幕（桌面）、开启视频（摄像头）和开启麦克风（麦克风）。为了能够准确访问相关设备，我们需要获取相关设备的名称。`ffmpeg`支持通过设备名称访问设备。有两种方法可以访问设备名称（以Windows端为例）

1. 打开Windows端的【设备管理器】，查看：【音频输入与输出】得到麦克风名称，【摄像头】获取摄像头名称
2. 在命令行中输入：`ffmpeg -list_devices true -f dshow -i dummy`，得到设备名称列表

得到相关设备名称后，即可进行硬件设备的数据推流，相关指令如下：

- **摄像头推流**：`ffmpeg -f dshow -i video="${camera-name}" -vcodec libx264 -preset:v ultrafast -tune:v zerolatency -f flv rtmp://127.0.0.1:1935/live/home`
- **麦克风推流**：`ffmpeg -f dshow -i audio="${microphone-name}" -vcodec libx264 -preset:v ultrafast -tune:v zerolatency -f flv rtmp://127.0.0.1:1935/live/home`
- **摄像头&麦克风推流**：`ffmpeg -f dshow -i video="${camera-name}" -f dshow -i audio="${microphone-name}" -vcodec libx264 -preset:v ultrafast -tune:v zerolatency -f flv rtmp://127.0.0.1:1935/live/home`
- **屏幕推流**：`ffmpeg -f gdigrab -i desktop -vcodec libx264 -preset:v ultrafast -tune:v zerolatency -f flv rtmp://127.0.0.1:1935/live/home`
- **屏幕&麦克风推流***：`ffmpeg -f *gdigrab* -i "1:0" -vcodec libx264 -preset ultrafast -acodec libmp3lame -ar 44100 -ac 1 -f flv rtmp://127.0.0.1:1935/rtmplive/home`
- **屏幕&麦克风&摄像头**：`ffmpeg -f avfoundation -framerate 30 -i "1:0" \-f avfoundation -framerate 30 -video_size 640x480 -i "0" \-c:v libx264 -preset ultrafast \-filter_complex 'overlay=main_w-overlay_w-10:main_h-overlay_h-10' -acodec libmp3lame -ar 44100 -ac 1 -f flv rtmp://localhost:1935/rtmplive/home`

注意，上述命令仅作为测试时的参考，用于确定`nginx rtmp`相关配置及`ffmpeg`配置成果情况，实际应当参考相关需求设置`ffmpeg`参数。

## 推拉流测试(Linux端)
> 上课的时候被老师建议用`linux`来搭建系统QAQ……虽然之前尝试过，但是在做推流测试的时候踩了大坑，遂半途弃坑……但是觉得还是逃不掉，不如勇敢面对吧。

（跑路了，左转`WebRTC.md`→_→）


# 参考内容

1. `ffmpeg`基础：[A quick guide to using FFmpeg to convert media files | Opensource.com](https://opensource.com/article/17/6/ffmpeg-convert-media-file-formats)
2. `windows`系统下载`ffmpeg`及环境配置：[Windows下载FFmpeg最新版（踩了一上午的坑终于成功） - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/390924591)
3. `windows`端搭建`nginx rtmp`服务器：[Windows 搭建 nginx RTMP 服务器 - fengMisaka - 博客园 (cnblogs.com)](https://www.cnblogs.com/linuxAndMcu/p/12517787.html#:~:text=%E6%8C%89%E4%BD%8F%20windows%20%E9%94%AE%20%2BR%EF%BC%8C%E8%BE%93%E5%85%A5%20cmd%EF%BC%8C%E8%BF%9B%E5%85%A5%20cmd%20%E5%91%BD%E4%BB%A4%E7%AA%97%E5%8F%A3%EF%BC%8C%E8%BF%9B%E5%85%A5,nginx%20%E7%9B%AE%E5%BD%95%EF%BC%9A%20cd%20E%3Atechnology%5B%26ng%26%5Dinx-1.17.9%20%EF%BC%8C%E7%84%B6%E5%90%8E%E5%90%AF%E5%8A%A8%20nginx%20rtmp%20%E6%9C%8D%E5%8A%A1%E5%99%A8%EF%BC%9A)
4. `python`中`ffmpeg-video-streaming`包：[python-ffmpeg-video-streaming · PyPI](https://pypi.org/project/python-ffmpeg-video-streaming/)，相关文档参考：[Python FFmpeg Video Streaming - Quick Start (aminyazdanpanah.com)](https://video.aminyazdanpanah.com/python/start?r=dash)
5. `ffmpeg`推拉流测试：[Windows 搭建 nginx rtmp服务器 - microsoftzhcn - 博客园 (cnblogs.com)](https://www.cnblogs.com/sntetwt/p/11435564.html)
6. 前端`flv.js`拉流介绍：[视频直播知识之四：直播DEMO——RTMP推流和HTTP-FLV拉流 | murphylee blog (seminelee.com)](https://seminelee.com/2021/06/20/video-4/)
7. `linux`端的`nginx`部署：[通过 nginx 搭建一个基于 http-flv 的直播流媒体服务器 – 92IT🍀](http://123.57.164.21/?p=1458)
8. `ffmpeg`常用推流指令：[FFmpeg常用推流命令 - 简书 (jianshu.com)](https://www.jianshu.com/p/d541b317f71c)
