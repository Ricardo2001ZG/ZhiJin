import psutil
import threading
import json
import time
import os
import socketio
import socket

# 服务器地址及端口号
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 8888

# 心跳间隔时间（秒）
HEARTBEAT_INTERVAL = 60

# 最多重试次数
MAX_RETRY_COUNT = 3

# 获取实例信息
def get_instance_info():
    # 获取 CPU 信息
    cpu_info = "{} {}".format(psutil.cpu_count(logical=False), psutil.cpu_freq().max)
    # 获取内存信息
    memory_info = "{} GB".format(round(psutil.virtual_memory().total / 1024**3, 2))
    # 获取硬盘信息
    workdir = get_work_dir()
    disk_name, disk_usage = get_disk_info(workdir)
    disk_info = "{} GB / {} GB".format(round(disk_usage.used / 1024**3, 2),
                                       round(disk_usage.total / 1024**3, 2))
    # 获取 IP 地址
    ip_address = socket.gethostbyname(socket.gethostname())
    # 构建实例信息字典
    instance_info = {
        "cpu": cpu_info,
        "memory": memory_info,
        "disk": disk_info,
        "ip_address": ip_address,
        # 其他需要上传的信息
    }
    return instance_info

# 获取工作路径
def get_work_dir():
    workdir = "/tmp"
    if os.path.exists("config"):
        with open("config", "r") as f:
            for line in f:
                line_split = line.strip().split("=")
                if line_split[0] == "workdir":
                    workdir = line_split[1].strip()
                    break
    
    if not workdir:
        if os.name == "nt":  # Windows 系统
            workdir = os.getenv("TEMP", os.path.abspath("./tmp"))
        else:  # Linux/MacOS 系统
            workdir = "/tmp"
    
    print("Work directory:", workdir)
    return workdir

# 获取硬盘信息
def get_disk_info(path):
    usage = psutil.disk_usage(path)
    total = usage.total
    used = usage.used
    free = usage.free
    name, _ = os.path.splitdrive(path)
    disk_name = name if name else "/"
    return disk_name, psutil._common._sdiskusage(total, used, free)

# 获取服务器地址及端口号
def get_server():
    host = DEFAULT_SERVER_HOST
    port = DEFAULT_SERVER_PORT
    if os.path.exists("config"):
        with open("config", "r") as f:
            for line in f:
                line_split = line.strip().split("=")
                if line_split[0] == "host":
                    host = line_split[1].strip()
                elif line_split[0] == "port":
                    port = int(line_split[1].strip())

    if not (1 <= port <= 65535):
        raise ValueError("端口号必须在 1 和 65535 之间！")
    
    return (host, port)

# 构建心跳包
def build_heartbeat_package(uuid):
    heartbeat = {
        "uuid": uuid,
        "timestamp": int(time.time())
    }
    return json.dumps(heartbeat)

# 发送心跳包
def send_heartbeat(sio, uuid):
    retry_count = 0
    while retry_count <= MAX_RETRY_COUNT:
        try:
            # 构建心跳包
            heartbeat_package = build_heartbeat_package(uuid)
            # 发送心跳
            sio.emit("heartbeat", heartbeat_package)
            # 等待 HEARTBEAT_INTERVAL 秒后再发送下一次心跳
            time.sleep(HEARTBEAT_INTERVAL)
            retry_count = 0
        except Exception as e:
            print("发送心跳失败：{}".format(e))
            retry_count += 1
            if retry_count > MAX_RETRY_COUNT:
                print("无法连接服务器！")

# 处理指令
def handle_commands(sio):
    @sio.on("command")
    def on_command(data):
        try:
            # 解析指令
            command = json.loads(data)
            if command["type"] == "build":
                # 处理构建指令
                project_name = command["project_name"]
                git_url = command["git_url"]
                # 返回信息告知服务器开始执行指令
                result = {"status": "running",
                          "message": "开始构建 {} 项目（Git URL: {}）...".format(project_name, git_url)}
                sio.emit("command_result", json.dumps(result))
                # TODO: 执行构建操作
                # 返回信息告知服务器指令执行成功或失败
                result = {"status": "success",
                          "message": "构建任务已完成！"}
                sio.emit("command_result", json.dumps(result))
            elif command["type"] == "test":
                # 处理测试指令
                project_name = command["project_name"]
                # 返回信息告知服务器开始执行指令
                result = {"status": "running",
                          "message": "开始测试 {} 项目...".format(project_name)}
                sio.emit("command_result", json.dumps(result))
                # TODO: 执行测试操作
                # 返回信息告知服务器指令执行成功或失败
                result = {"status": "success",
                          "message": "测试任务已完成！"}
                sio.emit("command_result", json.dumps(result))
            else:
                print("无法识别的指令：{}".format(command))
        except Exception as e:
            print("处理指令失败：{}".format(e))

# 建立 websocket 连接，并保持心跳连接以及接收指令
def connect_to_server():
    try:
        # 获取服务器地址及端口号
        server_host, server_port = get_server()
        # 建立 websocket 连接
        sio = socketio.Client()
        sio.connect("http://{}:{}".format(server_host, server_port))
        # 发送实例信息
        instance_info = get_instance_info()
        instance_info_package = json.dumps(instance_info)
        sio.emit("instance_info", instance_info_package)
        # 接收 UUID
        @sio.on("uuid")
        def on_uuid(data):
            uuid = json.loads(data)["uuid"]
            print("UUID：{}".format(uuid))
            # 启动心跳线程
            heartbeat_thread = threading.Thread(target=send_heartbeat, args=(sio, uuid))
            heartbeat_thread.start()
            # 处理指令
            handle_commands(sio)

        sio.wait()
    except Exception as e:
        print("连接服务器失败：{}".format(e))


# 下面代码仅作演示用途
import signal

def main():
    # 建立 websocket 连接，并保持心跳连接以及接收指令
    sio = connect_to_server()

    # 注册 Ctrl-C 信号处理函数
    def signal_handler(sig, frame):
        print("用户取消！")
        if sio.sid:
            print("正在安全断开连接，请稍等...")
            # 向服务端发送掉线请求
            sio.emit("disconnect_request")
            # 开启倒计时
            count_down = 5
            while count_down > 0:
                print("倒计时 {} 秒...".format(count_down))
                time.sleep(1)
                count_down -= 1
                if not sio.sid:
                    print("已断开连接！")
                    return
            print("未能安全断开连接，请注意数据安全！")
            return
        else:
            print("未连接服务器，直接退出。")
            sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    main()
