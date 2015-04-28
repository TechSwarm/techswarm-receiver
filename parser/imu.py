from parser.parser import BaseParser
from parser.timestamp import get_timestamp


class IMUParser(BaseParser):
    def __init__(self):
        self.gyro = None
        self.accel = None
        self.magnet = None
        self.pressure = None

    def parse(self, data_id, *values):
        values = [int(x) for x in values]
        if data_id == '$GYRO':
            self.gyro = values
        elif data_id == '$ACCEL':
            self.accel = values
        elif data_id == '$MAGNET':
            self.magnet = values
        elif data_id == '$MBAR':
            self.pressure = values[0]
        else:
            return False

        if all([self.gyro, self.accel, self.magnet, self.pressure]):
            # todo send it instead of just printing
            print(self.generate_data())
            self.gyro = self.accel = self.magnet = self.pressure = None

        return True

    def generate_data(self):
        return {
            'timestamp': get_timestamp(),

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
