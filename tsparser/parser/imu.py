from tsparser.parser import BaseParser
from tsparser import config, sender, planetarydata


def uint2int(value):
    #vprint("converting %d" % value)
    if value < 32768:
        return value
    else:
        return value - 65536

class IMUParser(BaseParser):
    url = config.URL + '/imu'

    def __init__(self):
        self.gyro = None
        self.accel = None
        self.magnet = None
        self.pressure = None

    def parse(self, line, data_id, *values):
        if data_id == '$MBAR':
            self.pressure = self.validate_values(values, 1, 'MBAR')[0]
        else:
            if data_id == '$GYRO':
                self.gyro = [uint2int(x) for x in self.validate_values(values, 3, 'GYRO')]
            elif data_id == '$ACCEL':
                self.accel = [uint2int(x) for x in self.validate_values(values, 3, 'ACCEL')]
            elif data_id == '$MAGNET':
                self.magnet = [uint2int(x) for x in self.validate_values(values, 3, 'MAGNET')]
            else:
                return False

        if all([self.gyro, self.accel, self.magnet, self.pressure]):
            data = self.generate_data()
            sender.send_data(data, IMUParser.url)
            planetarydata.Calculator().on_data_update('imu', data)
            self.gyro = self.accel = self.magnet = self.pressure = None

        return True

    @staticmethod
    def validate_values(values, num, data_id):
        """
        Utility function to check number of values provided and convert them to
        ints.

        :param num: expected number of values
        :param data_id: data ID (like GYRO, ACCEL, etc.) to show in case of
            error
        """
        if len(values) != num:
            raise ValueError('{} must provide {} values'.format(data_id, num))
        return [int(x) for x in values]

    def generate_data(self):
        return {
            'timestamp': BaseParser.timestamp,

            'gyro_x': self.gyro[0],
            'gyro_y': self.gyro[1],
            'gyro_z': self.gyro[2],

            'accel_x': self.accel[0],
            'accel_y': self.accel[1],
            'accel_z': self.accel[2],

            'magnet_x': self.magnet[0],
            'magnet_y': self.magnet[1],
            'magnet_z': self.magnet[2],

            'pressure': self.pressure
        }
