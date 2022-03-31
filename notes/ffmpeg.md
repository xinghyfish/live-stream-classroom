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

## 推流直播实现思路

1. 调用摄像头获取音频和图像
2. 将视频分割为帧
3. 将每一帧进行需求加工后
4. 将此帧写入pipe管道
5. 利用ffmpeg进行推流直播

- 环境配置：

1. `nginx`服务器
2. `nginx-rtmp-module`
3. `ffmpeg`

# 参考内容

1. [A quick guide to using FFmpeg to convert media files | Opensource.com](https://opensource.com/article/17/6/ffmpeg-convert-media-file-formats)
2. [Windows下载FFmpeg最新版（踩了一上午的坑终于成功） - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/390924591)
3. [Windows 搭建 nginx RTMP 服务器 - fengMisaka - 博客园 (cnblogs.com)](https://www.cnblogs.com/linuxAndMcu/p/12517787.html#:~:text=%E6%8C%89%E4%BD%8F%20windows%20%E9%94%AE%20%2BR%EF%BC%8C%E8%BE%93%E5%85%A5%20cmd%EF%BC%8C%E8%BF%9B%E5%85%A5%20cmd%20%E5%91%BD%E4%BB%A4%E7%AA%97%E5%8F%A3%EF%BC%8C%E8%BF%9B%E5%85%A5,nginx%20%E7%9B%AE%E5%BD%95%EF%BC%9A%20cd%20E%3Atechnology%5B%26ng%26%5Dinx-1.17.9%20%EF%BC%8C%E7%84%B6%E5%90%8E%E5%90%AF%E5%8A%A8%20nginx%20rtmp%20%E6%9C%8D%E5%8A%A1%E5%99%A8%EF%BC%9A)
4. [python-ffmpeg-video-streaming · PyPI](https://pypi.org/project/python-ffmpeg-video-streaming/)
