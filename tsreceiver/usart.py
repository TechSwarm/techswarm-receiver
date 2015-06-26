import serial
import array
import tsreceiver.config as config

class Usart:
    """
    Usart class implement communication with USART device,
    receiving records and photos
    """
    def __init__(self):
        self.uart_connection = serial.Serial(config.SERIAL_DEVICE_NAME, config.BAUDRATE)
        #self.uart_connection = open("/home/piotr/testinput", "rb")

    def readline(self):
        """
        Read next line from serial device
        :return: line of input from serial device
        :rtype: bytes
        """
        return self.uart_connection.readline()

    def get_photo_as_bytearray(self, width, height):
        """
        :param width: width of image in pixels
        :type width: int
        :param height: height of image in pixels
        :type height: int
        :return: photo as byte array encoded in RGB565
        :rtype: bytearray
        """
        # skip all headers

        print("Entering byte reading mode")	

        input_data = self.uart_connection.read(config.PHOTO_PACKET_SIZE*2 + 2)
        try:
            while input_data.decode("utf-8").find(config.PHOTO_HEADER) != -1:
                input_data = self.uart_connection.read(config.PHOTO_PACKET_SIZE*2 + 2)
        except UnicodeDecodeError:
            pass

        photo = array.array('B')
        for i in range(2*320*240):
            photo.append(0)

        lastx = -1
        lasty = -1
        for i in range(16*240):
            print("Byte reading", lasty / 240 * 100, "%")
            if lasty > input_data[1]:
                break
            if lasty == input_data[1] and lastx >= input_data[0]:
                break
            lastx = input_data[0]
            lasty = input_data[1]

            for j in range(40):
                photo[input_data[1]*640 + input_data[0]*40 + j] = input_data[2 + j]

            if input_data[0] == 15 and input_data[1] == 239:
                break

            input_data = self.uart_connection.read(config.PHOTO_PACKET_SIZE*2 + 2)

        print("Exiting byte reading mode")
        return photo

