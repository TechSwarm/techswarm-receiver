from tsparser.parser import BaseParser
from tsparser.sender import send_data
from tsparser import config


class GPSParser(BaseParser):
    url = config.URL + '/gps'

    def __init__(self):
        self.data = {}

    def parse(self, line, data_id, *values):
        if data_id not in ['$GPGGA', '$GPGSA', '$GPGSV', '$GPRMC', '$GPVTG']:
            return False

        if not _checksum_valid(line):
            raise ValueError('Calculated GPS checksum does not equal the one '
                             'provided in output')
        values = list(values)
        # Remove checksum from last value
        values[-1] = values[-1][:values[-1].rindex('*')]

        if data_id == '$GPGGA':  # Fix data
            (_,  # UTC timestamp
             latitude, latitude_dir,
             longitude, longitude_dir,
             quality, satellites, hdop,
             altitude, _,  # Altitude unit (always meters)
             _, _,  # Geoidal separation - value and unit (not used)
             _, _  # Diff. station last update time and ID (not used)
             ) = values
            if int(quality) == 0:  # no fix
                self.data.update({
                    'quality': 'no_fix',
                    'active_satellites': int(satellites)
                })
            else:
                self.data.update({
                    'latitude': _parse_latitude(latitude, latitude_dir),
                    'longitude': _parse_longitude(longitude, longitude_dir),
                    'quality': _parse_quality(quality),
                    'active_satellites': int(satellites),
                    'hdop': float(hdop),
                    'altitude': float(altitude)
                })
        elif data_id == '$GPGSA':  # DOP and active satellites
            if int(values[1]) == 1:  # no fix
                self.data.update({
                    'fix_type': 'no_fix'
                })
            else:
                self.data.update({
                    'fix_type': _parse_fix_type(values[1]),
                    'pdop': float(values[-3]),
                    'hdop': float(values[-2]),
                    'vdop': float(values[-1])
                })
        elif data_id == '$GPGSV':  # Satellites in View
            self.data['satellites_in_view'] = int(values[2])
        elif data_id == '$GPRMC':  # Recommended Minimum (Pos, Vel, Time)
            if self.data['quality'] != 'no_fix':
                self.data.update({
                    'speed_over_ground': _parse_speed(values[6]),
                    'direction': float(values[7])
                })
        elif data_id == '$GPVTG':  # Velocity made good
            # Nothing interesting here, but it's the last message before the
            # next $GPGGA, so we can send the data we've obtained
            self.data['timestamp'] = BaseParser.timestamp
            if not send_data(self.data, self.url):
                pass
                # todo do something when transmission error occur
            print(self.data)
            self.data = {}
        return True


def _parse_latitude(latitude, latitude_dir):
    return _parse_coord(latitude, latitude_dir, 'N', 'S')


def _parse_longitude(longitude, longitude_dir):
    return _parse_coord(longitude, longitude_dir, 'E', 'W')


def _parse_coord(coord, coord_dir, positive_sign, negative_sign):
    """
    Convert coordinate to single float value, replacing degree minutes with
    decimal fraction and taking into consideration the direction specified

    :param coord: coordinate string
    :type coord: str
    :param coord_dir: direction
    :param positive_sign: direction when coordinate is positive
    :param negative_sign: direction when coordinate is negative
    :rtype: float
    """
    dot = coord.index('.')
    if coord_dir != positive_sign and coord_dir != negative_sign:
        raise ValueError("Coordinate direction '{}' is neither '{}' nor '{}'"
                         .format(coord_dir, positive_sign, negative_sign))

    sign = 1 if coord_dir == positive_sign else -1
    return sign * (float(coord[:dot - 2]) + float(coord[dot - 2:]) / 60)


def _parse_quality(quality):
    return ['no_fix', 'gps', 'dgps'][int(quality)]


def _parse_fix_type(mode):
    # I have literally no idea why quality is indexed from 0, but mode from 1
    return ['no_fix', '2d', '3d'][int(mode) - 1]


def _parse_speed(speed_in_knots):
    """Convert speed in knots to km/h"""
    return float(speed_in_knots) * 1.852


def _checksum_valid(line):
    """
    Calculate the checksum of the GPS output and check if it is equal to
    the provided checksum in output; therefore - there was no
    transmission errors.

    The checksum is XOR of all bytes between $ and * characters
    (excluding themselves).

    :param line: line of output to check
    :type line: str
    :return: True if the output is valid; False otherwise
    :rtype: bool
    """
    l = line.index('$')
    r = line.rindex('*')
    chksum = 0
    for char in line[l + 1: r]:
        chksum ^= ord(char)
    if line[r + 1: r + 3] == '%.2X' % chksum:
        return True
    return False
