from threading import Lock
from datetime import datetime

from tsparser.timestamp import DT_FORMAT


class Logger:
    """
    Class responsible for simple logging. Logger requires module name for each message and it's possible to get filtered
    logs. Logger is also thread safe.
    """

    def __init__(self, log_filename=None):
        """
        :param log_filename: name of file which the log will be saved to or None if such a file should not exist
        :type log_filename: str
        :return:
        """
        self.__logfile_handle = open(log_filename, 'a') if log_filename else None
        self.__logs = list()
        self.__modules_names = set()
        self.__data_mutex = Lock()

    def log(self, module_name, message):
        """
        Log a message.

        :param module_name: name of module which logs a message
        :type module_name: str
        :param message: message to be logged
        :type message: str
        """
        log_entry = (datetime.now(), module_name, message)
        self.__save_log_entry_to_file(log_entry)
        self.__data_mutex.acquire()
        self.__logs.append(log_entry)
        self.__modules_names.add(module_name)
        self.__data_mutex.release()

    def get_logs(self, module_filter=None):
        """
        Get all logged messages, optionally filter them by modules.

        :param module_filter: list of selected modules' names. If None, don't filter.
        :type module_filter: list
        :return: list of tuples containing logs, each tuple format: (datetime_timestamp, module_name, message)
        :rtype: list
        """
        if module_filter is None:
            module_filter = self.get_all_modules()
        self.__data_mutex.acquire()
        chosen_logs = [log_entry for log_entry in self.__logs if log_entry[1] in module_filter]
        self.__data_mutex.release()
        return chosen_logs

    def get_all_modules(self):
        """
        Get list of all registered modules. Module is registered when it logs a message for its very first time.

        :return: set of all registered modules.
        :rtype: set
        """
        self.__data_mutex.acquire()
        modules_names = set(self.__modules_names)
        self.__data_mutex.release()
        return modules_names

    def clear_logs(self):
        """
        Clears internal log buffer releasing occupied memory. Logs saved on disk are kept.
        """
        self.__data_mutex.acquire()
        self.__logs.clear()
        self.__modules_names.clear()
        self.__data_mutex.release()

    def __save_log_entry_to_file(self, log_entry):
        if self.__logfile_handle is None:
            return
        timestamp = log_entry[0].strftime(DT_FORMAT)
        module_name = log_entry[1]
        message = log_entry[2]
        self.__logfile_handle.write('{}|{}|{}\n'.format(timestamp, module_name, message))
