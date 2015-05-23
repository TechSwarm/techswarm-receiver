from abc import ABCMeta, abstractmethod


class BaseParser(metaclass=ABCMeta):
    timestamp = None

    @abstractmethod
    def parse(self, line, data_id, *values):
        """
        Take one line of probe's input and interpret it.

        :param line: the line of output without any changes
        :type line: str
        :param data_id: type of data to be quickly identified by parsers
            (actually, the substring before the first comma)
        :type data_id: str
        :param values: values from output after being comma-split
        :type values: str
        :return: True if the parser consumed the given output (so it should
            not be parsed by the rest of the parsers); False otherwise
        :rtype: bool
        """


class ParseException(Exception):
    """
    Raised when an error occurred during parsing the output. Usually means a
    transmission error.
    """
    pass


from tsparser.parser.gps import GPSParser
from tsparser.parser.imu import IMUParser
from tsparser.parser.photo import PhotoParser
from tsparser.parser.sht import SHTParser
