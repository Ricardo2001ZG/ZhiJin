# AutoBuild 🛠️

AutoBuild 是一个 Python 项目，旨在为开发者提供自动构建、部署和测试等功能。它可以与常见的版本控制工具（如 Git 和 SVN）结合使用，并支持使用 Fastbuild 等工具进行软件构建。

**该项目还在开发中！功能展示并不代表实际可用** 👷‍♂️

## ⚙️ 功能介绍
---

### 实例控制 💻

本功能是基于 WebSocket 的分布式系统中的客户端程序，可以通过与服务端建立 WebSocket 连接，并保持心跳连接以及接收指令来实现。程序主要功能包括：

1. 获取本地机器的实例信息，并发送给服务端。
2. 接收服务端下发的指令，并根据不同的指令类型执行相应的操作，最后将执行结果反馈给服务端。
3. 支持在终端按下 Ctrl-C 取消按钮时，自动判断客户端是否已经连接上服务端，如果没有连接则直接退出，如果连上服务端则尝试安全断开连接。

此外，还提供其他辅助函数，如获取服务器地址及端口号、获取工作路径、获取硬盘信息等。

### 部署项目 🚀

本功能它可以通过检查目标项目是否存在和可读性来确保项目的有效性，并下载和解压缩安装软件包。此外，还提供了拉取项目代码的功能，并支持在Git和SVN之间进行选择。

1. 检查指定路径是否存在以及是否可读
2. 支持下载安装包，并且自行解压
3. 自动安装 Git 和 SVN环境
4. 支持 git 或者 svn 拉取项目代码

- 实例控制：将机器硬件等信息上传至中心控制服务器，并接收控制服务器下发的指令。
- 部署项目：通过 git 或 svn 部署项目到指定的工作文件夹中，并自行维护更新。
- 执行命令/编译：使用 Fastbuild 等工具来构建项目的产物。
- 上传产物：编译结束后的产物能够被上传到指定位置，支持其他第三方 SDK 上传设置。
- 清理工作：将编译结束后的临时垃圾进行清理。

### 执行编译 📦

本功能主要用于自动化地编译和构建代码。可以根据传入的参数，自动执行编译命令和构建命令，并实时打印构建进度。

主要包含以下功能：

1. 检查编译环境是否符合要求
2. 更改当前工作目录为项目根目录
3. 执行编译命令
4. 计算构建进度百分比，并实时打印构建进度
5. 检查构建结果，返回构建状态信息

### 上传产物 ⬆️

本功能实现了上传产物的功能，可以将指定目录下的文件上传到指定的服务器上。
**TODO**


## 🚀 快速上手

### 启动服务端和被控端
1. 请确保**服务端,客户端,被控端**电脑已经有安装好[Python 3.10](https://www.python.org/downloads/release/python-3100/)或者更高版本的Python

2. 然后进行依赖库的安装
```bash
pip install -r requirements.txt
```

3. 启动服务端
> 这里为了跟现有的Flask 应用集成,给出的是以API形式,具体文件在 `websocket_server_api.py`
> 你需要在你自己的Flask应用内集成他,或者参考`demo_server.py`代码
```bash
python demo_server.py
```

4. 启动被控端
> 注意:不能有中文路径!
创建一个 config 文件写入服务端的IP和Port

```
host=localhost
port=5000
```
启动被控端
```bash
python agent.py
```

5. 查看输出
此时服务端的输出应该如下
```
例 09e7737c-f718-11ed-ad1a-9e565be2af5a 已连接到控制中心！
实例信息： {'cpu': 'Intel64 Family 6 Model 85 Stepping 4, GenuineIntel 2', 'memory': '16.0 GB', 'disk': '52.32 GB / 60.0 GB', 'ip_address': '172.30.113.141', 'name': 'WINDOWS', 'uuid': '09e7737c-f718-11ed-ad1a-9e565be2af5a', 'last_heartbeat': 1684591813, 'connected_at': '2023-05-20 22:10:13', 'sid': 'x9PgkStgCyL_aXV9AAAB', 'state': 'connected'}
当前终端实例列表： {'09e7737c-f718-11ed-ad1a-9e565be2af5a': {'cpu': 'Intel64 Family 6 Model 85 Stepping 4, GenuineIntel 2', 'memory': '16.0 GB', 'disk': '52.32 GB / 60.0 GB', 'ip_address': '172.30.113.141', 'name': 'WINDOWS', 'uuid': '09e7737c-f718-11ed-ad1a-9e565be2af5a', 'last_heartbeat': 1684591813, 'connected_at': '2023-05-20 22:10:13', 'sid': 'x9PgkStgCyL_aXV9AAAB', 'state': 'connected'}}
09e7737c-f718-11ed-ad1a-9e565be2af5a 绑定 x9PgkStgCyL_aXV9AAAB 客户端
```

被控端输出如下
```
Work directory: C:\Users\ADMINI~1\AppData\Local\Temp
UUID：09e7737c-f718-11ed-ad1a-9e565be2af5a
```

在服务端上打开[http://127.0.0.1:5000](http://127.0.0.1)可以看到实例列表如下

![instances](./assests/instances.png)


### 执行任务
首先先跟服务端连接上

```python
# 创建 SocketIO 客户端实例
sio = socketio.Client()

# 连接服务器
sio.connect("http://localhost:5000")
```

目前只有处理有限指令,比如 
* `get_instances`: 获取实例信息
* `pull`: 部署或者更新项目
* `build`: 构建项目

执行指令需要两个部分
下面以部署项目为例子

1. 构建指令
构建指令需要元素如下
* `command`: 这个是给具体执行指令的被控端使用,里面包含需要执行指令的数据
* `type`: 指令的类型
* `uuid`: 执行该指令机器的UUID
* `callback`: 回调事件名称,如果指令执行完毕之后需要发送数据回来,则会发送结果到`callback`处

那么整个的指令应该是这样子
```python
# command 是被实例执行需要的数据
command = {
    "type": "pull",
    "project_name": "ZhiJin",
    "url": "https://github.com/Ricardo2001ZG/ZhiJin.git",
    "branch": "main"
}

# 将指令封装好发给服务端
data = {
    "command": command,
    "uuid": "UUID of machine",
    "callback": "pull_result" # 回调函数
}

sio.emit("command", json.dumps(data),callback=callback_command)
```


2. 定义回调事件
在我们发送指令之后,如果需要获取指令完成之后的数据
则需要设置一个回调函数,告知服务端在指令完成之后将数据发到指定的回调事件

**注意**:不同的指令返回的格式并不通用,具体可以看 `websocket_server_api.py`中的代码
```python
# 处理 pull_result 事件，并输出服务器返回的 pull 结果
@sio.on("pull_result")
def handle_pull_result(data):
    global FINSH,PROJECT_PATH

    # 将 JSON 格式的字符串转换为 Python 对象
    result = json.loads(data)

    # 输出 pull 结果信息
    print("Pull 结果：")
    print("返回代码：", result["code"])
    print("返回信息：", result["message"])
    
    # 更新项目的路径
    PROJECT_PATH = result['project_path']
    FINSH = True
```

至此,整个快速上手内容已经讲完,更多使用的细节可以参考 `demo.py` (或者将`demo.py`喂给new bing也行)