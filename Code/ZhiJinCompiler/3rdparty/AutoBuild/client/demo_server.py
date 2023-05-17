from threading import Lock
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import time
import uuid

# 心跳间隔时间（秒）
HEARTBEAT_INTERVAL = 2

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# 维护的终端实例列表
# 存储客户端信息的字典（key 为 uuid，value 为 实例信息 + sid）
instances = {}

# 为线程加锁
thread_lock = Lock()

# 处理心跳包
def heartbeat(data):
    # 获取数据
    uuid_value = data.get("uuid")
    # 查找对应的实例
    with thread_lock:
        if uuid_value in instances:
            instance = instances[uuid_value]
            # 更新最后一次心跳时间
            instance["last_heartbeat"] = int(time.time())
        else:
            print("未知 UUID：{}".format(uuid_value))

# 处理终端实例注册请求
def register_instance(data):
    # 生成 UUID
    uuid_value = str(uuid.uuid1())
    # 添加信息
    instance_info = data["instance_info"]
    instance_info["uuid"] = uuid_value
    instance_info["last_heartbeat"] = int(time.time())
    instance_info["connected_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    instance_info["sid"] = request.sid
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
                del instances[uuid]
                print("实例 {} 与客户端 {} 断开连接！".format(uuid, request.sid))
                socketio.emit("instance_disconnected", {"uuid": uuid}, to=uuid)
                break

# 注册终端实例
@socketio.on('register_instance')
def handle_register_instance(data):
    uuid_value = register_instance(data)
    emit('registered', {"uuid": uuid_value},room = request.sid)

# 接收终端实例发送来的心跳包数据
@socketio.on('heartbeat')
def handle_heartbeat(data):
    heartbeat(data)

# 返回终端实例列表
@app.route('/')
def index():
    return render_template('index.html', instances=instances)

if __name__ == '__main__':
    # 启动清理线程
    cleanup_thread = threading.Thread(target=cleanup_instances)
    cleanup_thread.start()
    # 启动应用
    socketio.run(app, debug=True)
