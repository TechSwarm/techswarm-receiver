from tsreceiver.usart import Usart
from tsreceiver import config
from tsparser.timestamp import get_timestamp


def receive():

    # raw dump file
    raw = open(config.RAW_NAME, 'a')

    usart = Usart()

    while True:
        line = usart.get()
        line = line + ',' + get_timestamp() + '\n'
        raw.write(line)
        raw.flush()
