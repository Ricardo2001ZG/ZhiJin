import os
import time
import re
import datetime
import json
import argparse
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

STOP = False

class FileWatcher(FileSystemEventHandler):
    def __init__(self, filename,  remote_url=None):
        """
        构造函数，初始化各种属性
        :param filename: 需要监控的文件名
        :param remote_url: 远程服务器 URL，可选参数
        """
        self.filename = filename
        self.regex = re.compile(
             r'^(\d+)\s+job_name\s+\'([^\']+)\'\s+stats\s+(process|success|failed|cache)\s+location\s+((?:\d{1,3}\.){3}\d{1,3})\s+buildTime\s+(\d+)'
        )
        self.regex_matches = []
        self.remote_url = remote_url  # 添加远程服务器 URL 属性
        self.headers = {"Content-Type": "application/json"}
    
    def on_modified(self, event):
        """
        监听到文件有修改时触发的回调函数
        :param event: 文件系统事件对象
        """
        if event.src_path == self.filename:
            with open(self.filename) as f:
                # Process new content
                for line in f.readlines():
                    match = self.regex.search(line)
                    if match:
                        timestamp, name, stats, location, buildtime = match.groups()
                        self.regex_matches.append((timestamp, name, stats, location, buildtime))
                        print(f"time: {self.convert_date(timestamp)}, name: {name}, stats: {stats}, location: {location}, buildtime: {buildtime}")

                        # send data to control server
                        data = {
                                    "time": self.convert_date(timestamp),
                                    "name": name,
                                    "stats": stats,
                                    "location": location,
                                    "buildtime": buildtime
                                }
                        json_data = json.dumps(data)
                        if self.remote_url:
                            response = requests.post(self.remote_url, data=json_data, headers=self.headers)
                            print(f"Response status code: {response.status_code}")
                    elif "STOP_BUILD" in line:
                        global STOP
                        STOP = True
                        print("Stopping file watcher...")
                        observer.stop()

    def convert_date(self,timestamp):
        """
        将时间戳转换为日期时间字符串
        :param timestamp: 时间戳
        :return: 格式化后的日期时间字符串
        """
        if not timestamp.isdigit():
            return "0-0-0-0 0:0:0"

        # GetCurrentFileTime函数返回的是100-nanosecond为单位的64位整数时间戳，需要转换成秒为单位
        # Windows文件时间戳从1601年1月1日起计算，需要减去相应的秒数与时区差值
        file_time_now = int(timestamp) / 10000000 - 11644473600 - time.timezone

        # 将时间戳转换为当前系统的时间
        # 时间戳是以当前系统的时区为准，而不是UTC时间
        local_time = datetime.datetime.utcfromtimestamp(file_time_now)

        # 格式化输出为2023-05-08 17:14:48 CST格式的字符串
        return local_time.strftime("%Y-%m-%d %H:%M:%S")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File watcher that monitors changes in a specified file.")
    parser.add_argument("-f", "--filename", type=str, default=None, help="path to the file being watched")
    args = parser.parse_args()
    filename = args.filename
    if filename is None:
        temp_dir = os.environ.get("TEMP", "/tmp")
        filename = os.path.join(temp_dir, "FastBuild", "FastBuildLog.log")
    event_handler = FileWatcher(filename)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(filename), recursive=False)
    observer.start()
    print("BIG BROTHER IS WATCHING YOU")
    try:
        while not STOP:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
