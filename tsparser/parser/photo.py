import subprocess
from tsparser.parser import BaseParser
from tsparser import config, sender


class PhotoParser(BaseParser):
    url = config.URL + '/photos'

    def parse(self, line, data_id, *values):
        if data_id == '$PHOTO':
            if len(values) != 1:
                raise ValueError('{} must provide {} values'
                                 .format(data_id, 1))
            try:
                raw_photo = open(values[0], mode='rb')
                raw_photo_content = raw_photo.read()
                raw_photo.close()
                rgb_photo_content = PhotoParser.get_rgb_from_bytearray(raw_photo_content, 320)
                rgb_photo = open(values[0] + ".txt", mode="wb")
                rgb_photo.write(rgb_photo_content)
                rgb_photo.close()
                subprocess.call(["convert", values[0] + ".txt", values[0] + ".jpg"])
                jpg_photo = open(values[0] + ".jpg", mode="rb")
                jpg_photo_content = jpg_photo.read()
                jpg_photo.close()
            except IOError:
                return

            data = {'timestamp': BaseParser.timestamp}
        else:
            return False

        sender.send_data(data, PhotoParser.url, jpg_photo_content)

        return True

    @staticmethod
    def get_rgb_from_bytearray(bytearray, width):
        """
        Convert little endian bytearray in RGB565 format to binary PPM
        :param bytearray: array with RGB656 encoded pixels
        :type bytearray: bytearray
        :param width: width of image
        :type width: int
        :return: PPM file as string
        :rtype: bytearray
        """
        result = b'# ImageMagick pixel enumeration: 320,240,255,srgb\n'

        for i in range(0, len(bytearray), 2):
            # little endian
            b1 = bytearray[i + 1]
            b2 = bytearray[i]
            # RGB565 parsing
            # first 5 bits of b1
            color_R = (b1 >> 3 ) << 3
            # 3 last bits of b1 and 3 first bits of b2
            color_G = (((b1 & 7) << 3) + (b2 >> 5)) << 2
            # 5 last bits of b2
            color_B = (b2 & 31) << 3

            # add row to result
            row = "{},{}: ({},{},{})\n".format((i//2)%width, (i//2)//width,
                                               color_R, color_G, color_B)
            result += row.encode("utf-8")

        return result

