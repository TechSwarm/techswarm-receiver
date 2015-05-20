from queue import Queue

from tsreceiver.pusher import Pusher
from tsreceiver.usart import Usart
from tsreceiver import config
from tsparser.timestamp import get_timestamp

def receive():
    lines_queue = Queue()
    push_thread = Pusher(lines_queue)
    push_thread.start()

    # raw dump file
    raw = open(config.RAW_NAME, 'a')

    usart = Usart()

    while True:
        try:
            line = usart.get()
        except:
            break
        line = line + ',' + get_timestamp() + '\n'
        raw.write(line)
        lines_queue.put(line)

    #push_thread.join()
