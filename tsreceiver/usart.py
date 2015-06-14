import serial
import tsreceiver.config as config

class Usart:
    """
    Usart class implement communication with USART device,
    receiving records and photos
    """
    def __init__(self):
        self.uart_connection = serial.Serial(config.SERIAL_DEVICE_NAME, config.BAUDRATE)

    def readline(self):
        """
        Read next line from serial device
        :return: line of input from serial device
        :rtype: bytes
        """
        return self.uart_connection.readline()
