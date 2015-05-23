from threading import Thread, Lock
from time import sleep

from tsparser import config, sender
from tsparser.parser import GPSParser, IMUParser, SHTParser
from tsparser.timestamp import get_timestamp
from tsparser.utils.singleton import Singleton


class Calculator(metaclass=Singleton):
    url = config.URL + '/planet'
    DATA_CALCULATOR_QUEUE = (
        # Remember! Each entry has access to results of entries above
        # Format: (result_name, method)
        # Method gets two dicts as arguments: first obtained from parsers,
        #   second contains already calculated parameters. Method should
        #   return result.
    )

    def __init__(self):
        self.__OBTAINED_DATA_SCHEME = {
            GPSParser: None,
            IMUParser: None,
            SHTParser: None
        }
        self.__obtained_data = dict(self.__OBTAINED_DATA_SCHEME)
        self.__data_mutex = Lock()
        Thread(target=self.__calculator_thread, daemon=True).start()

    def on_data_update(self, source, data):
        self.__data_mutex.acquire()
        self.__obtained_data[source] = data
        self.__data_mutex.release()

    def __calculator_thread(self):
        while True:
            self.__data_mutex.acquire()
            if all(self.__obtained_data):
                timestamp = get_timestamp()
                obtained_data = self.__obtained_data
                self.__obtained_data = dict(self.__OBTAINED_DATA_SCHEME)
                self.__data_mutex.release()  # Do *NOT* block on_data_update method!

                calculated_data = self.__calculate_data(obtained_data)
                calculated_data['timestamp'] = timestamp
                sender.send_data(calculated_data, self.url)

            if self.__data_mutex.locked():
                self.__data_mutex.release()
            sleep(0.01)

    @staticmethod
    def __calculate_data(obtained_data):
        calculated_data = dict()
        for result_name, calc_method in Calculator.DATA_CALCULATOR_QUEUE:
            result = calc_method(obtained_data, calculated_data)
            calculated_data[result_name] = result
        return calculated_data

    # calculators