import types
import unittest
from unittest.mock import patch

from tsparser import main


DEFAULT_TIMESTAMP = '2015-01-01T12:00:00.000000'


class ParserTestCase(unittest.TestCase):
    """
    TestCase subclass which adds a few utilities to make testing parsers easier.

    The class adds functions to pass piece of output to parsers as well as
    patches the send_data function, so no data is actually sent to the server,
    although it can be checked whether the data that would be sent is correct.
    """

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


def _parse_output(self, output):
    """
    Pass the output, line by line, to the parsers
    :type output: str
    """
    for line in output.splitlines():
        if line:
            self.parse_line(line)
