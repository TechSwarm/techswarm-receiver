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
            'temperature': 20.0,
            'humidity': 43.5
        }
        sender.send_data(fake_data, SHTParser.url)
        planetarydata.Calculator().on_data_update(SHTParser, fake_data)
        return True
