import socketio
import json
import time


# 创建 SocketIO 客户端实例
sio = socketio.Client()

# 连接服务器
sio.connect("http://localhost:5000")

# 实例列表
INSTANCES = []

# 项目的物理路径
PROJECT_PATH = None

# 当前任务的ID(会随着不同指令执行而变化)
TASK_ID = None

# 上一条指令完成的信号
FINSH = False

def callback_command(*data):
    if len(data) == 0:
        return
    else:
        result = data[0]
        if isinstance(result,str):
            result = json.loads(result)
        if result['code'] != 0:
            print(f"指令执行失败! 失败码: {result['code']} \t 失败信息: {result['message']}")
        else:
            # 更新任务ID
            if 'id' in result.keys():
                TASK_ID = result['id']
            print(f"指令发送成功!回复信息: {result['message']}")

# 处理 instance_list 事件，并发送 pull 命令请求
@sio.on("instance_list")
def handle_instance_list(data):
    global INSTANCES,FINSH
    # 将 JSON 格式的字符串转换为 Python 对象
    instance_list = json.loads(data)

    # 遍历实例列表，并输出每个实例的信息
    for instance in instance_list:
        print("UUID：", instance["uuid"])
        print("状态：", instance["state"])
        print("连接时间：", instance["connected_at"])
        print("最后心跳时间：", instance["last_heartbeat"])
        print("IP：", instance["ip_address"])
        print("CPU：", instance["cpu"])
        print("内存：", instance["memory"])
        print("磁盘：", instance["disk"])
        print("-------------------------------")
    INSTANCES = instance_list
    FINSH = True
    return 

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

# 处理 build_result 事件,并输出构建信息
@sio.on("build_result")
def handle_build_result(data):
    global FINSH

    # 将 JSON 格式的字符串转换为 Python 对象
    result = json.loads(data)
    if result['type'] == 'progress':
        print(f"收到构建信息 序号:{result['seq']} \t 消息:{result['message']}")
    else:
        # 标记已经完成构建
        FINSH = True
        print("/n/n/n详细的构建日志如下:")
        print("+---------------------------------+")
        print(result['message'])
        print("+---------------------------------+")


# 发送 get_instances 事件请求
FINSH = False
sio.emit("get_instances")

# 等待指令完成
while not FINSH:
    time.sleep(0.1)

# 遍历实例列表，查找当前状态为 "connected" 的实例，并选择第一个实例
chosen_instance = None
for instance in INSTANCES:
    if instance["state"] == "connected":
        chosen_instance = instance
        break

# 如果没有当前状态为 "connected" 的实例，则抛出异常
if not chosen_instance:
    raise Exception("No online instances available")

# 构造要发送的命令数据
command = {
    "type": "pull",
    "project_name": "ZhiJin",
    "url": "https://github.com/Ricardo2001ZG/ZhiJin.git",
    "branch": "main"
}
data = {
    "command": command,
    "uuid": chosen_instance["uuid"],
    "callback": "pull_result"
}

# 发送带有 UUID 的 pull 命令请求
FINSH = False
sio.emit("command", json.dumps(data),callback=callback_command)

# 等待指令完成
while not FINSH:
    time.sleep(0.1)

if PROJECT_PATH == None:
    raise Exception("cannot not get project path on instance machine")
command = {
    "type":"build",
    "project_dir":PROJECT_PATH,
    "build_command":"cd .\\Code\\ZhiJinCompiler\\3rdparty\\fastbuild\\Code && FBuild.exe -clean -monitor -summary -j2 FBuild-x64-Release",
}

data = {
    "command": command,
    "uuid": chosen_instance["uuid"],
    "callback": "build_result"
}

# 发送构建指令
FINSH = False
sio.emit("command",json.dumps(data),callback=callback_command)
# 等待指令完成
while not FINSH:
    time.sleep(0.1)

# 等待事件响应
# sio.wait()

# 关闭 SocketIO 连接
sio.disconnect()