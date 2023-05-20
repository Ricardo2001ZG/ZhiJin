from threading import Lock
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import time
import uuid
from datetime import datetime
from common import send_event_with_retry,LIFOQueue

# 心跳间隔时间（秒）
HEARTBEAT_INTERVAL = 10

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
# socketio = SocketIO(app)
socketio = SocketIO(app,logger=True, engineio_logger=True)

# 维护的终端实例列表
# 存储客户端信息的字典（key 为 uuid，value 为 实例信息 + sid）
instances = {}

# 维护的构建返回信息
# Key 为任务ID，value 为 data 的 LIFOQueue 数组
# data 格式如下
# {
# time: 构建时间
# name: 构建目标名称
# stats: 有四种情况:
#         a. process 构建中
#         b. cache 命中缓存
#         c. failed 构建失败
#         d. success 构建成功
# location: 编译机器的IP地址
# buildtime: 构建花费时间
#}
build_log = {}

# 为线程加锁
thread_lock = Lock()
build_log_lock = Lock()

# 处理心跳包
def heartbeat(data_json):
    data = json.loads(data_json)
    # 获取数据
    uuid_value = data["uuid"]
    # 查找对应的实例
    with thread_lock:
        if uuid_value in instances:
            instance = instances[uuid_value]
            # 更新最后一次心跳时间
            instance["last_heartbeat"] = int(time.time())
        else:
            print("未知 UUID：{}".format(uuid_value))

# 处理终端实例注册请求
def register_instance(data:dict):
    ## 查看是否需要重新注册
    if 'uuid' in data.keys():
        with thread_lock:
            uuid_value = data['uuid']
            ## 如果已经有存在的uuid,则无需重新注册
            if uuid_value in instances.keys():
                return uuid_value

    # 生成 UUID
    uuid_value = str(uuid.uuid1())
    # 添加信息
    print(f"接收的实例信息: {data}")
    instance_info = data
    instance_info["uuid"] = uuid_value
    instance_info["last_heartbeat"] = int(time.time())
    instance_info["connected_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    instance_info["sid"] = request.sid
    instance_info['state'] = 'connect'
    # 添加到实例列表中
    with thread_lock:
        instances[uuid_value] = instance_info
        print("实例 {} 已连接到控制中心！".format(uuid_value))
        print("实例信息：", instance_info)
        print("当前终端实例列表：", instances)
    return uuid_value

# 清理断开连接的实例
def cleanup_instances():
    while True:
        # 每隔 HEARTBEAT_INTERVAL 秒清理一次断开连接的实例
        time.sleep(HEARTBEAT_INTERVAL)
        expired_instances = []
        with thread_lock:
            if len(instances.keys()) == 0 :
                continue
            for uuid, instance in instances.items():
                last_heartbeat = instance["last_heartbeat"]
                if time.time() - last_heartbeat > HEARTBEAT_INTERVAL * 2:
                    # 如果该实例超过两倍心跳间隔时间没有发送心跳包，就认为它已经断开连接
                    expired_instances.append(uuid)
            # 移除断开连接的实例
            for uuid in expired_instances:
                if uuid in instances:
                    del instances[uuid]
                    print("实例 {} 已断开连接！".format(uuid))
                    socketio.emit("instance_disconnected", {"uuid": uuid}, to=uuid)
            if expired_instances:
                print("当前终端实例列表：", instances)


# 客户端连接时的操作
@socketio.on('connect')
def on_connect():
    # 返回信息告知连接成功
    emit('connected', {'data': 'Connected'}, room=request.sid)

# 处理客户端断开连接事件
@socketio.on("disconnect")
def handle_disconnect():
    print("客户端 {} 断开连接！".format(request.sid))
    with thread_lock:
        for uuid, instance in list(instances.items()):
            if instance["sid"] == request.sid:
                instance['state'] = 'disconnect'
                # del instances[uuid]
                print("实例 {} 与客户端 {} 断开连接！".format(uuid, request.sid))
                # socketio.emit("instance_disconnected", {"uuid": uuid}, to=uuid)
                break


# 注册终端实例
@socketio.on('register_instance')
def handle_register_instance(data):
    uuid_value = register_instance(json.loads(data))
    uuid_data = {"uuid": uuid_value}
    print(f"{uuid_value} 绑定 {request.sid} 客户端")
    if not send_event_with_retry('registered', json.dumps(uuid_data),room = request.sid):
        print("返回注册消息失败！")

# 接收终端实例发送来的心跳包数据
@socketio.on('heartbeat')
def handle_heartbeat(data):
    heartbeat(data)

# 返回终端实例列表
@app.route('/')
def index():
    print("+-------------------------------")
    print(instances)
    print("+-------------------------------")
    # 转换实例心跳时间戳为日期
    with thread_lock:
        for key in instances.keys():
            instances[key]['last_heartbeat_date'] =  datetime.fromtimestamp(instances[key]['last_heartbeat']).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', instances=instances)


# 触发测试代码
@socketio.on('test_module')
def handle_test_model(data):
    print("触发测试代码")
    # 构建指令
    command = {
        "type":"build",
        "id": str(uuid.uuid1()),
        "project_name":"Zhijin",
        "git_url":"https://github.com/Ricardo2001ZG/ZhiJin",
    }
    if not send_event_with_retry('command',json.dumps(command),room = request.sid):
        print("发送构建指令失败")

    time.sleep(10)

    # 测试指令
    command = {
        "type":"test",
        "project_name":"Zhijin",
        "id": str(uuid.uuid1()),
    }
    if not send_event_with_retry('command',json.dumps(command),room = request.sid):
        print("发送测试指令失败")

# 执行指令回复
@socketio.on('command_result')
def handle_command_result(data):
    data = json.loads(data)

    # 拉取项目指令回复
    if data['type'] == "pull":
        if data['code'] != 0:
            print(f"拉取项目 {data['project_name']}\t 失败: {data['error']}")
        else:
            # 成功直接打印返回的消息
            print(f"{data['message']}")
    # 构建指令进度回复
    elif data['type'] == "progress":
        task_id = data["id"]
        seq = data["seq"]
        with build_log:
            if task_id not in build_log.keys():
                build_log[task_id] = LIFOQueue()
        # 因为Queue类型本身就是线程安全,不需要额外在锁内操作
        build_log[task_id].put(data['message'])
        print(f"已接收任务ID {task_id} 第 {seq} 份进度回馈")
    elif data["type"] == "build":
        print(f"任务ID: {data['id']} \t任务结果: {data['message']}\t 是否成功: {data['status']}")
    else:
        print(f"未知指令回复 {data['type']}")
    

if __name__ == '__main__':
    # 启动清理线程
    # cleanup_thread = threading.Thread(target=cleanup_instances)
    # cleanup_thread.start()
    # 启动应用
    socketio.run(app, debug=True,port=8888)