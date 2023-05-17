import os
import threading
import socket
import requests

# 产物
class Artifact:
    def __init__(self, file_path, upload_file_name, upload_url):
        self.file_path = file_path  # 文件路径
        self.upload_file_name = upload_file_name  # 上传后的文件名
        self.upload_url = upload_url  # 上传服务器 URL


# 上传产物
def upload_artifact(artifact_path, server_url):
    print("开始上传产物 {} ...".format(artifact_path))
    try:
        # 打开文件并读取二进制数据
        with open(artifact_path, 'rb') as f:
            artifact_data = f.read()
        # 发送 HTTP POST 请求上传文件
        response = requests.post(server_url, data=artifact_data)
        # 判断上传是否成功
        if response.status_code == 200:
            print(f"上传产物 {artifact_path} 成功！")
            return True
        else:
            print("上传产物失败：{}".format(response.text))
            return False
    except Exception as e:
        print("上传产物失败：{}".format(str(e)))
        return False

# 定义上传文件的生成器函数
def upload_artifacts(artifacts):
    if not isinstance(artifacts, list):
        artifacts = [artifacts]

    for artifact in artifacts:
        print(f"开始上传 {artifact.upload_file_name}")
        yield upload_artifact(artifact.file_path, artifact.upload_url)
