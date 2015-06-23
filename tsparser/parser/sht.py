from tsparser.parser import BaseParser
from tsparser import config, sender, planetarydata


class SHTParser(BaseParser):
    url = config.URL + '/sht'

    def __init__(self):
        self.temperature = None
        self.humidity = None

    def parse(self, line, data_id, *values):
        if data_id == '$TERM':
            self.temperature = -46.851 + ((175.72/65536) * self.validate_values(values, 1, 'TERM')[0])
        else:
            if data_id == '$HYDR':
                self.humidity = -6 + ((125/65536) * self.validate_values(values, 1, 'HYDR')[0])
            else:
                return False

        if all([self.temperature, self.humidity]):
            data = self.generate_data()
            sender.send_data(data, SHTParser.url)
            planetarydata.Calculator().on_data_update('sht', data)
            self.temperature = self.humidity = None
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

            'temperature': self.temperature,
            'humidity': self.humidity
        }
