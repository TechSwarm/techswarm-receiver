from tsparser import config
from tsparser.parser import BaseParser, ParseException
from tsparser.imu import IMUParser


def parse(input_file=None):
    """
    Parse the file specified as input.

    :param input_file: file to read input from. If None, then pipe specified
        in config is used
    :type input_file: file
    """
    if input_file is None:
        input_file = open(config.PIPE_NAME, 'r')

    parsers = [
        IMUParser()
    ]

    while True:
        line = input_file.readline()
        if not line:
            continue

        values = line.split(',')
        BaseParser.timestamp = values.pop().split("\n")[0]
        for parser in parsers:
            if parser.parse(line, *values):
                break
        else:
            raise ParseException('Output line was not parsed by any parser: {}'
                                 .format(line))
