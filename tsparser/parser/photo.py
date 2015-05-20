from tsparser.parser import BaseParser
from tsparser import config, sender


class PhotoParser(BaseParser):
    url = config.URL + '/photos'

    def parse(self, line, data_id, *values):
        if data_id == '$PHOTO':
            if len(values) != 1:
                raise ValueError('{} must provide {} values'
                                 .format(data_id, 1))
            photo = open(values[0], mode='rb')
            photo_content = photo.read()
            photo.close()

            data = {'timestamp': BaseParser.timestamp}
        else:
            return False

        sender.send_data(data, PhotoParser.url, photo_content)

        return True
