from queue import Queue
from threading import Thread

import requests

from tsparser import config
from tsparser.utils import StatisticDataCollector


send_queue = Queue()


class Sender(Thread):
    def run(self):
        while True:
            data, url, file = send_queue.get()
            _send_data(data, url, file)
            StatisticDataCollector().on_request_sent((data, url))
            send_queue.task_done()


def send_data(data, url, file=None):
    """
    Add data to send to request queue

    :param data: data to send
    :type data: dict
    :param url: url where data are sent to
    :type url: str
    :param file: content of file to send as multiple encoded file
    :type file: bytearray
    """
    send_queue.put((data, url, file))
    StatisticDataCollector().on_new_request((data, url))


def _send_data(data, url, file=None):
    """
    Send data to server

    :param data: data to send
    :type data: dict
    :param url: url where data are sent to
    :type url: str
    :param file: content of file to send as multiple encoded file
    :type file: bytearray
    :return True if data have been sent successfully; False otherwise
    :rtype bool
    """
    try:
        if file is None:
            response = requests.post(url, data=data,
                                     auth=(config.USERNAME, config.PASSWORD))
        else:
            response = requests.post(url, data=data,
                                     auth=(config.USERNAME, config.PASSWORD),
                                     files={'photo': ("photo.jpg", file)})
    except Exception as err:
        StatisticDataCollector().get_logger().log('sender', '{}: {}'.format(err.__class__.__name__, err))
        return False
    return response.status_code == 201
