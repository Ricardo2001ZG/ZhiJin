from flask import Blueprint, Flask, request

from .get_file import get_file
from .message import *
from .submit_task import submit_task
from .run_task import run_task

routes = Blueprint('routes', __name__)

# 你好 谢谢 小笼包 再见
@routes.route('/get_state')
def get_server_state():
    state_response = {'resCode': 1, 'resMsg': '你好，谢谢，小笼包，再见'}
    return jsonify(state_response)

# 返回任务产生的文件列表
@routes.route("/return", methods=["POST"])
def handle_get_file():
    return generate_req_body(0, get_file(), "文件列表")


# 提交任务
@routes.route("/submitTask", methods=["POST"])
def handle_submit_task():
    req_json = request.get_json()
    task_id = submit_task(req_json)
    return generate_req_body(0, {'taskId': task_id}, 'Task submitted successfully')

# 执行任务
@routes.route("/run", methods=["POST"])
def handle_run_task():
    req_json = request.get_json()
    timestamp = run_task(req_json)
    return generate_req_body(0, {'timestamp': str(timestamp)}, 'Run task now')
