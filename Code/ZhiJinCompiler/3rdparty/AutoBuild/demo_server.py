from flask import Flask, render_template
from flask_socketio import SocketIO
from datetime import datetime

# 导入封装好的 socket_server_api.py
from websocket_server_api import socket_bp, create_app, start_threads
import websocket_server_api as websocker_API

app = Flask(__name__)

# 注册需要使用的 blueprint
app.register_blueprint(socket_bp)

# 初始化 socketio 实例
socketio = SocketIO(app)

if __name__ == '__main__':
    start_threads()
    app = create_app()
    # 删除 socket.run() 调用
    socketio.run(app, debug=False)

