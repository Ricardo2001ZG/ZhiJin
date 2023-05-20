import time
import threading

from flask_socketio import emit
import queue


def send_event_with_retry(event_name, message={}, max_retries=3, room=None):
    """
    发送消息给指定房间，并进行重试。

    :param event_name: 要发送的事件名称。
    :param message: 要发送的消息内容。默认为一个 JSON 对象。
    :param max_retries: 最大重试次数。默认为 3 次。
    :param room: 房间名称，如果指定了该参数，则将消息发送到指定的房间中。
    :return: 如果发送成功，返回 True；如果发送失败，则返回 False。
    """

    send_success = False
    retries = 0

    while not send_success and retries <= max_retries:
        try:
            if room is not None:
                emit(event_name, message, room=room, namespace='/')
            else:
                emit(event_name, message, namespace='/')

            send_success = True
        except Exception as e:
            retries += 1
            print(f'Failed to send message to room {room}. Retrying ({retries}/{max_retries})...')
            if retries > max_retries:
                return False

    return True


def send_with_retry(socket, module_name, message={}, max_retries=3, to=None):
    """
    发送消息给指定模块，并进行重试。

    :param socket: SocketIO 客户端对象。
    :param message: 要发送的消息内容。默认为一个 JSON 对象。
    :param module_name: 要发送的模块名称。
    :param max_retries: 最大重试次数。默认为 3 次。
    :param interval: 重试间隔时间，单位为秒。默认为 1 秒。
    :param to: 房间名称，如果指定了该参数，则将消息发送到指定的房间中。
    :return: 如果发送成功，返回 True；如果发送失败，则返回 False。
    """

    for retry in range(max_retries + 1):
        try:
            if to is not None:
                socket.emit(module_name, message, room=to)
            else:
                socket.emit(module_name, message)

            # 如果走到这里没有抛出异常，则说明发送成功
            return True
        except Exception as e:
            if retry < max_retries:
                print(f'Failed to send message to module {module_name}. Retrying ({retry + 1}/{max_retries})...')
            else:
                print(f'Failed to send message to module {module_name} after {max_retries} retries. Aborting...')
                return False


class LIFOQueue(queue.Queue):
    """继承 Queue 类型，实现 Last-In, First-Out (LIFO)的队列类型"""

    def _init(self, maxsize):
        self.queue = []

    def _put(self, item):
        """将数据插入到队列尾部"""
        self.queue.append(item)

    def _get(self):
        """消费队头数据，从队列头部弹出"""
        return self.queue.pop(0)

class Result:
    def __init__(self, code:int, error:str, message:str, **kwargs:dict):
        """
        :param code: 操作结果状态码
        :param error: 错误信息
        :param message: 操作结果信息
        :param kwargs: 其他返回参数，以字典方式传递
        """
        self.code = code
        self.error = error
        self.message = message
        for k, v in kwargs.items():
            setattr(self, k, v)

