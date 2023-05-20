import psutil
import threading
import json
import time
import os
import socketio
import socket
import platform
import sys
import datetime
import shutil
from common import send_with_retry
from deploy import pull_project
from build import compile_project
from watcher import FileWatcherManager


# 临时/工作目录
TEMP_DIR = os.environ.get("TEMP") or "./TMP"
# 检查临时目录是否存在
if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)


# 服务器地址及端口号
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 5000

# 心跳间隔时间（秒）
HEARTBEAT_INTERVAL = 10

# 心跳线程
HEARTBEAT_THREAD = None

# UUID 每个实例的标识符
UUID = ''

# 获取实例信息
def get_instance_info():
    # 获取 CPU 信息
    cpu_count = psutil.cpu_count(logical=False)
    cpu_type = platform.processor()
    cpu_info = "{} {}".format(cpu_type, cpu_count)    # 获取内存信息
    memory_info = "{} GB".format(round(psutil.virtual_memory().total / 1024**3, 2))
    # 获取硬盘信息
    workdir = get_work_dir()
    disk_name, disk_total, disk_used, disk_free, disk_usage = get_disk_info(workdir)
    disk_info = "{} GB / {} GB".format(round(disk_used / 1024, 2),
                                       round(disk_total / 1024, 2))
    # 获取 IP 地址
    ip_address = socket.gethostbyname(socket.gethostname())
    # 获取计算机名称
    name = get_computer_name()
    # 构建实例信息字典
    instance_info = {
        "cpu": cpu_info,
        "memory": memory_info,
        "disk": disk_info,
        "ip_address": ip_address,
        "name":name,
        # 其他需要上传的信息附加在这
    }
    return instance_info

def get_computer_name():
    if platform.system() == "Windows":
        return os.environ['COMPUTERNAME']
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        return socket.gethostname()
    else:
        return ""  # 其他操作系统不支持获取计算机名称

# 获取工作路径
def get_work_dir():
    workdir = None
    if os.path.exists("config"):
        with open("config", "r") as f:
            for line in f:
                line_split = line.strip().split("=")
                if line_split[0] == "workdir":
                    workdir = line_split[1].strip()
                    break
    
    if not workdir:
        if os.name == "nt":  # Windows 系统
            workdir = os.getenv(os.path.abspath("./TMP"))
        else:  # Linux/MacOS 系统
            workdir = "/tmp"
    
    print("Work directory:", workdir)
    return workdir

def get_disk_info(path):
    """
    获取指定路径所在的磁盘信息
    """
    try:
        usage = psutil.disk_usage(path)
        disk_name = path.split('\\')[0]
        disk_total = usage.total // (1024 * 1024) # MB
        disk_used = usage.used // (1024 * 1024) # MB
        disk_free = usage.free // (1024 * 1024) # MB
        disk_usage = usage.percent 
    except Exception as e:
        print("获取磁盘信息失败：{}".format(str(e)))
        disk_name, disk_total, disk_used, disk_free, disk_usage = '', 0, 0, 0, 0
    return disk_name, disk_total, disk_used, disk_free, disk_usage

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
def build_heartbeat_package():
    global UUID
    heartbeat = {
        "uuid": UUID,
        "timestamp": int(time.time())
    }
    return json.dumps(heartbeat)

# 发送心跳包,如果失败则一直尝试直到成功
def send_heartbeat(sio):
    retry_count = 0
    while True:
        try:
            # 构建心跳包
            heartbeat_package = build_heartbeat_package()
            # 发送心跳
            if not send_with_retry(socket=sio, module_name="heartbeat", message = heartbeat_package):
                raise Exception("cannot connect remote server")
            # sio.emit("heartbeat", heartbeat_package)
            # 等待 HEARTBEAT_INTERVAL 秒后再发送下一次心跳
            time.sleep(HEARTBEAT_INTERVAL)
        except Exception as e:
            print(f"发送心跳失败：{e} to {DEFAULT_SERVER_HOST}")
            time.sleep(3)

# 处理指令
def handle_commands(sio):
    @sio.on("command")
    def on_command(data):
        print(f"接收指令: {data}")
        try:
            # 解析指令
            command = json.loads(data)
            # 任务唯一ID
            task_id = command["id"]
            # 拉取项目
            if command['type'] == "pull":
                # 拉取的项目名称
                project_name = command['project_name']

                # 项目拉取地址
                repo_url = command['url']

                # 分支名称,默认为master
                branch = 'master'
                if 'branch' in command.keys():
                    branch = command['branch']

                # 是否指定commit ID
                commit_id = None
                if 'commit_id' in command.keys():
                    commit_id = command['commit_id']
                # 获取Git的可执行文件的路径
                # 从系统PATH环境变量中查找Git执行文件路径
                if os.name == "nt":
                    git_executable_name = "git.exe"
                else:
                    git_executable_name = "git"
                git_executable_path = shutil.which(git_executable_name)

                # 拉取并更新项目代码
                pull_result = pull_project(project_name, repo_url, branch, git_executable_path=git_executable_path)

                # 如果某个检查阶段失败,不会有 project_path 变量
                project_path = ""
                if "project_path" in dir(pull_result):
                    project_path = pull_result.project_path

                # 将信息返回给服务端
                result = {
                    "type":"pull",
                    "project_name":project_name,
                    "code":pull_result.code,
                    "message":pull_result.message,
                    "project_path":project_path,
                    "id":task_id,
                    "error":pull_result.error,
                }

                #Debug
                print(f"返回执行完毕后的指令结果给 command_result :{result}")
                if not send_with_retry(sio, "command_result", json.dumps(result)):
                    print("发送拉取指令结果结果失败")


            elif command["type"] == "build":
                # 处理构建指令
                project_dir = command["project_dir"]    # 项目的绝对路径
                build_command = command["build_command"]
                
                # 创建FileWatcherManager实例
                manager = FileWatcherManager()
                # 启动观察器
                watcher_thread = threading.Thread(target=manager.start)

                # 首先启动监视，再启动构建
                watcher_thread.start()

                # 流式获取构建信息进度并发送
                def send_progress(manager):
                    seq = 0 # 包的序列号
                    while True:
                        data = manager.get_data(timeout=1)
                        # 如果没有获取到数据并且observer线程已经退出，则跳出循环
                        if data is None and not manager.observer.is_alive():
                            break
                        
                        if data != None:
                            # 发送数据到服务端
                            result = {
                                "id":task_id,
                                "seq":seq,
                                "message":data,
                                "type":"progress"
                            }
                            send_with_retry(socket=sio,module_name="command_result",message=json.dumps(result))
                            seq+=1
                send_thread = threading.Thread(target=send_progress,args=(manager,))
                send_thread.start()

                # 获取构建日志
                build_result = compile_project(project_dir,build_command)
                status = False
                if "FBuild: OK" in build_result:
                    status = True

                result = {
                    "id":task_id,
                    "type":"build",
                    "message":build_result,
                    "status": status,
                }
                if not send_with_retry(sio, "command_result", json.dumps(result)):
                    print("发送构建指令结果失败")

                # 等待监视器和发送线程结束
                watcher_thread.join()
                send_thread.join()
            else:
                print("无法识别的指令：{}".format(command))
        except Exception as e:
            print("处理指令失败：{}\t 传递的指令元数据为: {}".format(e,data))


# 建立 websocket 连接，并保持心跳连接以及接收指令
def connect_to_server():
    connected = False  # 标记是否已经成功连接服务器
    while not connected:
        try:
            # 获取服务器地址及端口号
            server_host, server_port = get_server()
            # 建立 websocket 连接
            sio = socketio.Client()
            sio.connect("http://{}:{}".format(server_host, server_port))

            @sio.on("connected")
            def connect(data):
                # 重连
                reconnect_time = datetime.datetime.now()
                print(f"重连时间：{reconnect_time.strftime('%Y-%m-%d %H:%M:%S')}，本次重新连接成功。")

                # 重新发送实例信息给服务端
                global UUID
                if UUID != '':
                    instance_info = get_instance_info()
                    instance_info['uuid'] = UUID
                    instance_info_package = json.dumps(instance_info)
                    send_with_retry(socket=sio,module_name="register_instance", message=instance_info_package)

            # 发送实例信息
            instance_info = get_instance_info()
            instance_info_package = json.dumps(instance_info)
            send_with_retry(socket=sio,module_name="register_instance", message = instance_info_package)
            # 接收 UUID
            @sio.on("registered")
            def on_uuid(data):
                global UUID,HEARTBEAT_THREAD
                if(UUID != ''):
                    print(f"重新注册UUID值")
                UUID = json.loads(data)["uuid"]
                print("UUID：{}".format(UUID))
                # 创建心跳线程
                if HEARTBEAT_THREAD == None:
                    HEARTBEAT_THREAD = threading.Thread(target=send_heartbeat, args=(sio,))
                    HEARTBEAT_THREAD.start()
            # 注册处理指令
            handle_commands(sio)
            connected = True  # 成功连接，标记为 True
        except Exception as e:
            print("连接服务器失败：{}".format(e))
            time.sleep(5)  # 连接失败，等待 5 秒后重试
    return sio


# 下面代码仅作演示用途
import signal

def main():
    # 建立 websocket 连接，并保持心跳连接以及接收指令
    sio = connect_to_server()

    # 注册 Ctrl-C 信号处理函数
    def signal_handler(sig, frame):
        print("正在退出程序！")
        if sio.get_sid():
            print("正在安全断开连接，请稍等...")
            # 向服务端发送掉线请求
            if not send_with_retry(socket=sio,module_name="disconnect_request"):
                print("未能发送断开连接请求给服务端！")
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
            sys.exit()
        else:
            print("未连接服务器，直接退出。")
            sys.exit()

    # # 触发测试代码
    # send_with_retry(socket=sio,module_name='test_module',message={})

    signal.signal(signal.SIGINT, signal_handler)
    # sio.wait()

if __name__ == "__main__":
    main()
