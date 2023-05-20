import os
import re
import datetime
import json
import requests
from common import LIFOQueue
import queue
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileWatcher(FileSystemEventHandler):
    def __init__(self, filename, observer):
        """
        构造函数，初始化各种属性
        :param filename: 需要监控的文件名
        :param observer: 观察器对象
        """
        super().__init__()

        self.filename = filename
        self.regex = re.compile(r'^(\d+)\s+job_name\s+\'([^\']+)\'\s+stats\s+(process|success|failed|cache)\s+location\s+((?:\d{1,3}\.){3}\d{1,3})\s+buildTime\s+(\d+)')
        self.regex_matches = []
        self.data_queue = LIFOQueue()
        self.observer = observer

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
                        # print(f"time: {self.convert_date(timestamp)}, name: {name}, stats: {stats}, location: {location}, buildtime: {buildtime}")

                        data = {
                            "time": self.convert_date(timestamp),
                            "name": name,
                            "stats": stats,
                            "location": location,
                            "buildtime": buildtime
                        }
                        self.data_queue.put(data)

                    elif "STOP_BUILD" in line:
                        self.observer.stop()

    def convert_date(self, timestamp):
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


class FileWatcherManager:
    def __init__(self, filename=None):
        """
        构造函数，初始化各种属性
        :param filename: 需要监控的文件名,默认为 %TEMP%/FastBuild/FastBuildLog.log
        """
        if filename == None:
            # 从环境变量中获取临时文件夹的路径，如果不存在则默认使用/tmp目录
            temp_dir = os.environ.get("TEMP", "/tmp")

            # 组合得到日志文件的完整路径
            filename = os.path.join(temp_dir, "FastBuild", "FastBuildLog.log")
        self.filename = filename
        self.observer = Observer()
        self.event_handler = FileWatcher(self.filename, self.observer)

    def start(self):
        """
        启动文件监视器并开始监听文件系统事件
        """
        self.observer.schedule(self.event_handler, path=os.path.dirname(self.filename), recursive=False)
        self.observer.start()

    def stop(self):
        """
        停止文件监视器
        """
        self.observer.stop()
        self.observer.join()

    def get_data(self, block=True, timeout=None):
        """
        获取监视器读取到的数据
        :param block: 是否阻塞等待数据，默认为True，阻塞等待队列中有可用数据
        :param timeout: 设置阻塞等待的超时时间，默认为None，表示一直等待，直到队列中有可用数据
        """
        try:
            data = self.event_handler.data_queue.get(block=block, timeout=timeout)
            return data
        except queue.Empty:
            return None


# 判断模块是否为主模块，避免在被其它模块导入时执行以下代码
if __name__ == '__main__':
    # 从环境变量中获取临时文件夹的路径，如果不存在则默认使用/tmp目录
    temp_dir = os.environ.get("TEMP", "/tmp")

    # 组合得到日志文件的完整路径
    filename = os.path.join(temp_dir, "FastBuild", "FastBuildLog.log")

    # 创建FileWatcherManager实例
    manager = FileWatcherManager(filename)

    # 启动观察器
    manager.start()

    try:
        # 开始循环处理数据
        while True:
            # 调用get_data方法获取读取到的文件内容，
            # 如果timeout参数设置为1，则每次最多阻塞等待1秒钟
            data = manager.get_data(timeout=1)

            # 如果没有获取到数据并且observer线程已经退出，则跳出循环
            if data is None and not manager.observer.is_alive():
                break
            
            # TODO: 对获取到的数据进行一些处理，这里仅作占位符使用
            if data != None:
                print(data)
    except KeyboardInterrupt:
        # 异常处理，如果用户按下了Ctrl+C，则停止FileWatcherManager实例
        manager.stop()

    # 输出提示信息
    print("File watcher has stopped.")

