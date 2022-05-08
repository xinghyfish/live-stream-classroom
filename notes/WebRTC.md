# 基础知识
## 资料
- 教程参考：https://codelabs.developers.google.com/codelabs/webrtc-web#0

> WebRTC是真的快，有催人跑的意思。
调试完摄像头，连接成功后发现，`WebRTC`是真的快，比`ffmpeg`快多了。就决定是你了！

## 概述
WebRTC以`p2p`的方式工作，具体的内容为：
> WebRTC is designed to work peer-to-peer, so users can connect by the most direct route possible. However, WebRTC is built to cope with real-world networking: client applications need to traverse NAT gateways and firewalls, and peer to peer networking needs fallbacks in case direct connection fails.


# 问题记录
## 无法获取摄像头
按照教程操作时，没有显示出摄像头拍摄到的内容，通过console中的内容可以判断，是摄像头的问题。初步判断是没有摄像头权限。但是通过排查发现，Chrome设置中已经授权了访问请求，但是在设备列表中并没有发现摄像头选项。
之后，在终端输入：
```shell
$ cheese
```
上述命令调用系统摄像头，发现没有任何图像。因此，进一步判断是摄像头USB没有连接到虚拟机。查看USB：
```shell
$ lsusb
```
发现并没有摄像头设备。因此，在VMWare Workstation的菜单中选择【虚拟机】=>【设置】=>【USB控制器】=>【USB兼容性】，设置为【USB3.1】，同时在宿主系统（Win10）中打开运行`service.msc`，打开VMWare的USB服务，重启虚拟机后还是没有摄像头。到这一步可以确定虚拟机可以检测到摄像头了，但是尚未连接，因此在虚拟机工作站的菜单中选择`虚拟机 => 可移动设备`，已经可以摄像头，在右侧选择【连接（断开与主机的连接）】。
至此，问题解决。\~\(≧▽≦)/\~