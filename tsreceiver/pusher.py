import os
from threading import Thread
import time

from tsreceiver import config


class Pusher(Thread):
    def __init__(self, queue):
        Thread.__init__(self, daemon=True)
        """
        Create Pusher object to send data from given queue
        :param queue: queue of lines, which should be send to parser
        :type queue: queue
        """
        self.queue = queue
        if not os.path.exists(config.PIPE_NAME):
            os.mkfifo(config.PIPE_NAME)
        self.fifo = open(config.PIPE_NAME, 'w')

    def run(self):
        while True:
            #if self.queue.not_empty:
              #  line = self.queue.get()
             #   self.fifo.write(line)
            #else:
                time.sleep(1)


    def __del__(self):
        self.fifo.close()
