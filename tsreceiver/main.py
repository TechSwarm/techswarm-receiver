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
        if line.find(config.PHOTO_HEADER) is not -1:
            photo_RGB565 = usart.get_photo_as_bytearray(320, 240)
            timestamp = get_timestamp()
            try:
                photo_file = open(config.PHOTO_DIRECTORY + timestamp, "wb")
                photo_file.write(photo_RGB565)
                photo_file.close()
            except IOError:
                print("ERROR while writing photo")
                continue
            line = '$PHOTO,' + config.PHOTO_DIRECTORY + timestamp + ',' + timestamp +'\n'
            raw.write(line)
            raw.flush()

        else:
            line = str(line).strip('\r\n') + ',' + get_timestamp() + '\r\n'
            raw.write(line)
            raw.flush()
            # print(line)
