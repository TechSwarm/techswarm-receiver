from tsreceiver.usart import Usart
from tsreceiver import config
from tsparser.timestamp import get_timestamp


def receive():
    """
    Start receive data from serial device and write it to file
    """
    # raw dump file
    raw = open(config.RAW_NAME, 'a')

    usart = Usart()

    while True:
        try:
            rawline = usart.readline()
            line = rawline.decode("utf-8").strip("/n")
        except UnicodeDecodeError:
            print(rawline)
            print("line cannot be decoded\n")
            continue
        if line.find("$PHOTO") is not -1:
            pass
            # todo: implemet receiving photos
        else:
            line = str(line).strip('\r\n') + ',' + get_timestamp() + '\r\n'
            raw.write(line)
            raw.flush()
            # print(line)
