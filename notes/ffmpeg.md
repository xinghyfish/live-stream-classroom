# 知识预热

## 媒体文件

媒体文件的抽象组成：容器 ( *container* ) + 流 ( *stream* )

- 容器：将流封装起来，对外提供流的唯一**接口**
- 流：包含AV组件（语音+视频），使用编码方法对其进行编码

因此，选择合适的格式和容器来存储媒体文件就非常重要。FFmpeg 能够自动选择合适的格式和容器，而不需要进行复杂的配置。


## 基本转换

在命令行中使用`ffmpeg处理音频文件的基本格式如下：

```shell
ffmpeg -i input.mp3 output.ogg
```

使用`ffmpeg`命令，其中`input.mp3`表示输入文件，`output.ogg`表示转化为Vorbis语音流并封装在OGG容器中。对于视频文件的处理也有类似的命令：

```shell
ffmpeg -i input.mp4 output.webm
```



# 参考内容

1. [A quick guide to using FFmpeg to convert media files | Opensource.com](https://opensource.com/article/17/6/ffmpeg-convert-media-file-formats)
2. [Windows下载FFmpeg最新版（踩了一上午的坑终于成功） - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/390924591)
