from abc import ABCMeta, abstractmethod


class BaseParser(metaclass=ABCMeta):
    @abstractmethod
    def parse(self, data_id, *values):
        """
        Take one line of probe's input and interpret it.

        :param data_id: type of data to be quickly identified by parsers
            (actually, the substring before the first comma)
        :type data_id: str
        :param values: values from output after being comma-split
        :type values: str
        :return: True if the parser consumed the given output (so it should
            not be parsed by the rest of the parsers); False otherwise
        :rtype: bool
        """
