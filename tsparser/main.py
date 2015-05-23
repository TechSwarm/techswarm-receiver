from time import sleep
import traceback

from tsparser import config
from tsparser.parser import BaseParser, GPSParser, IMUParser, PhotoParser
from tsparser.sender import Sender
from tsparser.utils import StatisticDataCollector


def parse(input_file=None):
    """
    Parse the file specified as input.

    :param input_file: file to read input from. If None, then pipe specified
        in config is used
    :type input_file: file
    """
    StatisticDataCollector().get_logger().log('system', 'System has started!')
    Sender(daemon=True).start()
    if input_file is None:
        input_file = open(config.RAW_DATA_FILENAME, 'r')

    parsers = _get_parsers()
    while True:
        line = input_file.readline()
        if not line:
            sleep(0.01)
            continue
        _parse_line(parsers, line)


def _get_parsers():
    return [
        IMUParser(),
        GPSParser(),
        PhotoParser()
    ]


def _parse_line(parsers, line, catch_exceptions=True):
    StatisticDataCollector().on_new_received_data(line)
    values = line.split(',')
    BaseParser.timestamp = values.pop().strip()
    for parser in parsers:
        try:
            if parser.parse(line, *values):
                break
        except Exception:
            if catch_exceptions:
                StatisticDataCollector().get_logger().log(
                    parser.__class__.__name__, traceback.format_exc())
            else:
                raise
    else:
        error_message = 'Output line was not parsed by any parser: {}'.format(line)
        StatisticDataCollector().get_logger().log('system', error_message)
