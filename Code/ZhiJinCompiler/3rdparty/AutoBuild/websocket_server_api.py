from threading import Lock
import threading
from flask import Flask, render_template, request, Blueprint
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import time
import uuid
from datetime import datetime
from common import send_event_with_retry,LIFOQueue
import copy

# 心跳间隔时间（秒）
HEARTBEAT_INTERVAL = 10

socket_bp = Blueprint("socket", __name__)

socketio = SocketIO(logger=True, engineio_logger=True)

# 维护的终端实例列表
# 存储客户端信息的字典（key 为 uuid，value 为 实例信息 + sid）
instances = {}

# 维护的构建返回信息(TODO:改为Redis存储)
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

# 维护的执行指令的回调信息
# Key 为任务ID，value 格式如下
# {
#    "client": 发起任务的sid,
#    "type": 任务类型,
#    "callback": 回调给客户端的event name 
# }
task_progess = {}

# 为线程加锁
thread_lock = Lock()
build_log_lock = Lock()
task_progess_lock = Lock()

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
        uuid_value = data['uuid']
        with thread_lock:
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
    instance_info['state'] = 'connected'
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
@socket_bp.route('/')
def index():
    print("+-------------------------------")
    print(instances)
    print("+-------------------------------")
    # 转换实例心跳时间戳为日期
    with thread_lock:
        for key in instances.keys():
            instances[key]['last_heartbeat_date'] =  datetime.fromtimestamp(instances[key]['last_heartbeat']).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', instances=instances)


def callback_client(data:dict):
    # 根据任务登记表，将指令的回复数据返回给调用方
    task_id = data['id']

    with task_progess_lock:
        if task_id in task_progess.keys():
            task = task_progess[task_id]
            send_event_with_retry(event_name=task['callback'],message=json.dumps(data),room=task['client'])

# 执行指令回复
@socketio.on('command_result')
def handle_command_result(data):
    try:
        print(f"接收的指令回复元数据: {data}")
        data = json.loads(data)
        # 拉取项目指令回复
        if data['type'] == "pull":
            if data['code'] != 0:
                print(f"拉取项目 {data['project_name']}\t 失败: {data['error']}")
            else:
                # 成功直接打印返回的消息
                print(f"{data['message']}")
            # 发送一份给调用方
            callback_client(data)
            
        # 构建指令进度回复
        elif data['type'] == "progress":
            task_id = data["id"]
            seq = data["seq"]
            with build_log_lock:
                if task_id not in build_log.keys():
                    build_log[task_id] = LIFOQueue()
            # 因为Queue类型本身就是线程安全,不需要额外在锁内操作
            build_log[task_id].put(data['message'])
            print(f"已接收任务ID {task_id} 第 {seq} 个构建指令的回复")

            # 尝试发送一份给调用方(如果有指定回调函数)
            callback_client(data)

        # 构建指令执行完成
        elif data['type'] == "build":
            print(f"任务ID {data['id']} 构建完成")
            # 发送一份给调用方
            callback_client(data)
        else:
            print(f"未知任务类型: {data['type']}")
    except Exception as e:
        print("接收指令结果失败：{} \n接收指令回复的元数据为: {}".format(e,data))



# 主动获取构建指令的进度
@socketio.on('get_progress')
def handle_get_progess(data):
    data = json.loads(data)
    task_id = data['id']

    with build_log_lock:
        if task_id not in build_log.keys():
            return {'code': 404, 'message': 'Cannot find task id'}
        
    # 获取构建信息直到空为止
    logs = []
    progress_queue = build_log[task_id]
    while True:
        log = progress_queue.get()
        if log == None:
            break
        else:
            logs.append(log)
    return {'code':0,'message':f"Get {len(logs)} lines log","data":logs}
    


# 获取终端实例列表并返回
@socketio.on('get_instances')
def handle_get_instances():
    with thread_lock:
        instance_list = list(instances.values())
    send_event_with_retry(event_name='instance_list', message= json.dumps(instance_list))


# 通过uuid向实例发送命令并返回结果
@socketio.on('command')
def send_command_to_instance(data):
    data = json.loads(data)
    
    # 生成任务ID
    task_id = str(uuid.uuid1())
    command = data['command']
    command['id'] = task_id

    # 获取指定实力的UUID
    uuid_value = data['uuid']

    # 是否需要回馈信息
    callback = ""
    if "callback" in data.keys():
        callback = data["callback"]

    # 登记任务回馈
    with task_progess_lock:
        task_progess[task_id] = {
            "type":command["type"],
            "client":request.sid,
            "callback":callback,
        }

    # log task info
    print(f"新增任务ID：{task_id}\t 任务传递指令: {command}")

    with thread_lock:
        if uuid_value not in instances:
            data = {'code': 404, 'message': 'Instance not found or disconnected.'}
        else:
            try:
                if instances[uuid_value]['state'] != 'connected':
                    data = {'code': 301, 'message':"target agent is disconnect"}
                else:
                    sid = instances[uuid_value]['sid']
                    if send_event_with_retry(event_name='command',message=json.dumps(command), room=sid):
                        data = {'code': 0, 'message': 'Command sent.',"id":task_id}
                    else:
                        data = {'code':501, 'message':'Command send failed.'}
            except Exception as e:
                data = {'code': 500, 'message': str(e)}
    # 是否需要取消登记
    if data['code'] != 0:
        with task_progess_lock:
            del task_progess[task_id]
    return json.dumps(data)

# 启动清理线程(TODO:现不可用)
def start_threads():
    # 清理断开连接的实例线程
    # t1 = threading.Thread(target=cleanup_instances, args=())
    # t1.start()
    pass

# 创建 flask app
def create_app():
    # app config
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )

    # 注册 blueprint
    app.register_blueprint(socket_bp)

    # 初始化 socketio 实例
    socketio.init_app(app)
    return app

if __name__ == '__main__':
    start_threads()
    app = create_app()
    app.run(debug=True)