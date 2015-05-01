from tsparser.parser import BaseParser


class IMUParser(BaseParser):
    def __init__(self):
        self.gyro = None
        self.accel = None
        self.magnet = None
        self.pressure = None

    def parse(self, line, data_id, *values):
        if data_id == '$GYRO':
            self.gyro = [int(x) for x in values]
        elif data_id == '$ACCEL':
            self.accel = [int(x) for x in values]
        elif data_id == '$MAGNET':
            self.magnet = [int(x) for x in values]
        elif data_id == '$MBAR':
            self.pressure = int(values[0])
        else:
            return False

        if all([self.gyro, self.accel, self.magnet, self.pressure]):
            # todo send it instead of just printing
            print(self.generate_data())
            self.gyro = self.accel = self.magnet = self.pressure = None

        return True

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
