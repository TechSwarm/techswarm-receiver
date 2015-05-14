from queue import Queue
from threading import Thread

import requests

from tsparser import config
from tsparser.utils import StatisticDataCollector


send_queue = Queue()


class Sender(Thread):
    def run(self):
        while True:
            data, url = send_queue.get()
            _send_data(data, url)
            send_queue.task_done()
            StatisticDataCollector().on_request_sent((data, url))


def send_data(data, url):
    """
    Add data to send to request queue

    :param data: data to send
    :type data: dict
    :param url: url where data are sent to
    :type url: str
    """
    send_queue.put((data, url))
    StatisticDataCollector().on_new_request((data, url))


def _send_data(data, url):
    """
    Send data to server

    :param data: data to send
    :type data: dict
    :param url: url where data are sent to
    :type url: str
    :return True if data have been sent successfully; False otherwise
    :rtype bool
    """
    try:
        response = requests.post(url, data=data,
                                 auth=(config.USERNAME, config.PASSWORD))
    except requests.HTTPError:
        return False
    return response.status_code == 201
