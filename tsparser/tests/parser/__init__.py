import types
import unittest
from unittest.mock import patch

from tsparser import main


DEFAULT_TIMESTAMP = '2015-01-01T12:00:00.000000'


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        # Add functions to test parsers easily
        parsers = main._get_parsers()
        # Append timestamp so it does not have to be included in test data
        self.parse_line = lambda line: (
            main._parse_line(parsers, line + ',' + DEFAULT_TIMESTAMP))
        self.parse_output = types.MethodType(_parse_output, self)

        # Replace send_data with mock, so it does not actually send any data
        # nor need access to the internet, but we can check whether
        # the function was actually called
        self.patcher = patch('tsparser.sender.send_data')
        self.addCleanup(self.patcher.stop)
        self.send_data_mock = self.patcher.start()
        self.send_data_mock.return_value = True


def _parse_output(self, output):
    """
    Pass the output, line by line, to the parsers
    :type output: str
    """
    for line in output.splitlines():
        if line:
            self.parse_line(line)
