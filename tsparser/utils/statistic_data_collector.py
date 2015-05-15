from datetime import datetime
from threading import Lock

from tsparser import config
from tsparser.utils import Logger, Singleton


class StatisticDataCollector(metaclass=Singleton):
    """
    Thread-safe singleton destined for collecting statistic data.
    """

    def __init__(self):
        self.__start_time = datetime.now()
        self.__last_data_time = self.__start_time

        self.__bytes_received_this_second = 0
        self.__bytes_received_last_second = 0
        self.__total_bytes_received = 0

        self.__count_of_queued_requests = 0
        self.__total_count_of_sent_requests = 0

        self.__logger = Logger(config.LOG_FILENAME)
        self.__data_mutex = Lock()

    def on_new_received_data(self, data):
        """
        Method for calculating statistics.

        :param data: new received data
        :type data: str
        """
        now = datetime.now()
        self.__data_mutex.acquire()
        if self.__last_data_time.second != now.second:
            self.__bytes_received_last_second = self.__bytes_received_this_second
            self.__bytes_received_this_second = 0
        self.__last_data_time = now
        self.__bytes_received_this_second += len(data)
        self.__total_bytes_received += len(data)
        self.__data_mutex.release()

    def on_new_request(self, packet):
        """
        Method for calculating statistics.

        :param packet: packet prepared to be sent
        :type packet: tuple
        """
        self.__data_mutex.acquire()
        self.__count_of_queued_requests += 1
        self.__data_mutex.release()

    def on_request_sent(self, packet):
        """
        Method for calculating statistics.

        :param packet: sent packet
        :type packet: tuple
        """
        self.__data_mutex.acquire()
        self.__count_of_queued_requests -= 1
        self.__total_count_of_sent_requests += 1
        self.__data_mutex.release()

    def get_logger(self):
        """
        :return: logger
        :rtype: tsparser.utils.Logger
        """
        return self.__logger

    def get_time_since_last_data_receiving(self):
        """
        :return: time since last data receiving
        :rtype: datetime.timedelta
        """
        self.__data_mutex.acquire()
        time_since_last_data = datetime.now() - self.__last_data_time
        self.__data_mutex.release()
        return time_since_last_data

    def get_time_since_start(self):
        """
        :return: time since start
        :rtype: datetime.timedelta
        """
        return datetime.now() - self.__start_time

    def get_data_receiving_speed(self):
        """
        :return: count of received bytes in last second
        :rtype: int
        """
        self.__data_mutex.acquire()
        data_transfer_speed = self.__bytes_received_last_second
        self.__data_mutex.release()
        return data_transfer_speed

    def get_total_data_received(self):
        """
        :return: count of received bytes
        :rtype: int
        """
        self.__data_mutex.acquire()
        total_data_received = self.__total_bytes_received
        self.__data_mutex.release()
        return total_data_received

    def get_count_of_queued_requests(self):
        self.__data_mutex.acquire()
        queued_requests = self.__count_of_queued_requests
        self.__data_mutex.release()
        return queued_requests

    def get_total_count_of_sent_requests(self):
        self.__data_mutex.acquire()
        total_sent_requests = self.__total_count_of_sent_requests
        self.__data_mutex.release()
        return total_sent_requests
