# live-stream-classroom
综合项目实践项目学习记录+代码

> **关于作者**
> @name: 小黄鱼
> @email: xinghy.fish@qq.com

## 项目开发环境：
- 操作系统：`linux ubuntu 20.04`
- python解释器：`python3.8.6`
- IDE：`vscode`或者`pycharm`（vscode运行配置读取问题参考`notes/diary.md`）
- 数据库：`MySQL`
- 测试浏览器：`chrome`、`firefox`

## 项目结构
项目的代码结构如下：
```shell
live-stream-classroom
├─ .idea
├─ .vscode
│  └─ settings.json
├─ README.md
├─ demo
├─ notes
│  ├─ WebRTC.md
│  ├─ diary.md
│  ├─ ffmpeg.md
│  └─ nginx.md
├─ src
│  ├─ conf
│  │  └─ server.conf
│  ├─ controller
│  │  ├─ __init__.py
│  │  ├─ __pycache__
│  │  ├─ student.py
│  │  ├─ teacher.py
│  │  └─ websocket.py
│  ├─ main.py
│  ├─ model
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ static
│  │  ├─ avatars
│  │  ├─ css
│  │  ├─ demo
│  │  ├─ icons
│  │  ├─ images
│  │  ├─ js
│  │  └─ resources
│  └─ view
└─ venv
```

其中：
- `.idea`和`.vscode`是IDE的配置文件；
- `notes`文件夹为本项目进展过程中的一些技术摘要和日志；
- `README.md`文件为本文件；
- `src`存储项目的核心代码
- `venv`为项目的python虚拟环境

项目的核心代码文件`src`中，包含以下文件或文件夹：
- `conf`为服务器配置文件，包括项目的端口号等；
- `controller`存储tornado后端和数据库进行交互的组件，在MVC中表示控制器；
- `model`存储tornado中的模型文件，这里主要和数据库直接交互的模块`db`；
- `static`文件夹存储了项目的静态文件，例如`css`、`javascript`、`icons`、`resources`（程序运行中产生的中间文件，例如用户上传的文件、聊天记录、签到记录等）
- `demo`文件夹为隔离的测试环境，用于在正式继承功能前对技术核心的实践或代码的细节调试；
- `view`文件夹存储了视图相关的`html`文件
- `main.py`表示项目的程序入口，用于启动项目

## 项目的安装和启动
### 项目的安装
1. 使用git安装：打开存储项目的文件夹，在终端输入如下命令：
```bash
git clone https://github.com/xinghyfish/live-stream-classroom.git
```
即可安装。

2. 直接下载压缩包：点击[下载链接](https://github.com/xinghyfish/live-stream-classroom/archive/refs/heads/main.zip`)即可下载

### 项目运行配置
项目运行需要数据库支持，需要提前安装MySQL数据库。数据库的配置信息参考`src/model/db.py`中`get_conn()`函数，默认的用户名为`root`，密码为`123456`，数据库名为`online_teaching`，服务器为`127.0.0.1`，端口为默认端口`3306`。

连接数据库，若成功则数据库配置完成。

创建数据库后，需要创建数据库表：
- `SC`：学生选课表
- `TC`：教师授课表
- `course`：课程信息表
- `user`：用户信息表
  
上述各表的DDL如下：
```sql
create table course(
   id varchar(10) PRIMARY KEY,
   name varchar(16) NOT NULL,
   credit int NOT NULL,
   class varchar(30) NOT NULL,
   count int,
   ps varchar(500)
);

create table user(
   id int PRIMARY KEY AUTO_INCREMENT,
   username varchar(20) NOT NULL DEFAULT 'User',
   passwd varchar(20) NOT NULL DEFAULT '123456',
   nickname varchar(20),
   avatar blob,
   email varchar(40),
   school varchar(20),
   userID int,
   type char(6) NOT NULL DEFAULT '学生'
);

create table TC(
   teacherName varchar(16),
   courseID varchar(10),
   clock varchar(30),
   status int,
   PRIMARY KEY (teacherName, courseID, clock),
   FOREIGN KEY (teacherName) REFERENCES user(username),
   FOREIGN KEY (courseID) REFERENCES course(id)
);

create table SC(
   studentName varchar(16),
   courseID varchar(10),
   teacherName varchar(16),
   FOREIGN KEY (studentName) REFERENCES user(username),
   FOREIGN KEY (courseID) REFERENCES course(id),
   FOREIGN KEY (teacherName) REFERENCES user(username)
)
```

创建上述表后，即可运行项目。

### 项目运行
1. 打开文件夹`src`，将项目的python解释器指向`venv/bin/python3.8`。
2. 在图形化操作界面点击运行按钮或在终端中输入：
```bash
python main.py
```
如果没有错误，即说明项目运行成功。打开浏览器，在浏览器导航栏中输入：`127.0.0.1:8888`（`host:port`），即可运行项目。

## 项目问题和解决
项目开发中遇到的问题可以参考文件：`notes/diary.md`。

如果在部署项目时遇到问题或者发现程序中的bug欢迎在issue中提出并commit正确的版本。