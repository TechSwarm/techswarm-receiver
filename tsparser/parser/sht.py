from tsparser.parser import BaseParser
from tsparser import config, sender, planetarydata


class SHTParser(BaseParser):
    url = config.URL + '/sht'

    def __init__(self):
        pass

    def parse(self, line, data_id, *values):
        if data_id not in ['$TEMP', '$HUM']:  # temporary ids
            return False
        fake_data = {
            'temperature': 20.0,  # TODO ESI calculator assumes that
                                  # temperature is in Celsius degrees,
                                  # so fix that code when this is implemented
            'humidity': 43.5
        }
        sender.send_data(fake_data, SHTParser.url)
        planetarydata.Calculator().on_data_update('sht', fake_data)
        return True
