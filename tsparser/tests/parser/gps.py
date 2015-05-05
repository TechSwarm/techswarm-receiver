import unittest

from tsparser.parser import gps
from tsparser.tests.parser import DEFAULT_TIMESTAMP, ParserTestCase


class TestGPS(ParserTestCase):
    def test_gps_parser(self):
        """Test GPSParser with standard output (3D GPS fix)"""
        self.parse_output('''
$GPGGA,123519,4807.038,N,01130.000,E,1,08,0.9,545.4,M,46.9,M,,*46
$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
$GPGSV,2,1,08,01,40,083,46,02,17,308,41,12,07,344,39,14,22,228,45*75
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A''')
        self.assertEqual(self.send_data_mock.called, False)
        self.parse_line('$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48')
        self.send_data_mock.assert_called_with(
            {'timestamp': DEFAULT_TIMESTAMP,
             'latitude': 48.1173, 'longitude': 11.5, 'altitude': 545.4,
             'quality': 'gps', 'direction': 84.4, 'speed_over_ground': 41.4848,
             'fix_type': '3d', 'pdop': 2.5, 'hdop': 1.3, 'vdop': 2.1,
             'active_satellites': 8, 'satellites_in_view': 8},
            gps.GPSParser.url)

    def test_gps_parser_no_fix(self):
        """Test GPSParser when no fix is available"""
        self.parse_output('''
$GPGGA,002905.799,,,,,0,00,,,M,,M,,*71
$GPGSA,A,1,,,,,,,,,,,,,,,*1E
$GPRMC,002905.799,V,,,,,0.00,0.00,060180,,,N*4B''')
        self.assertEqual(self.send_data_mock.called, False)
        self.parse_line('$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32')
        self.send_data_mock.assert_called_with(
            {'timestamp': DEFAULT_TIMESTAMP, 'active_satellites': 0,
             'quality': 'no_fix', 'fix_type': 'no_fix'}, gps.GPSParser.url)


class TestGPSUtils(unittest.TestCase):
    def test_parse_latitude(self):
        self.assertAlmostEqual(gps._parse_latitude('3855.23816', 'N'),
                               38.920636, 4)
        self.assertAlmostEqual(gps._parse_latitude('3855.23816', 'S'),
                               -38.920636, 4)
        self.assertRaises(ValueError, gps._parse_latitude, '3855.23816', 'X')

    def test_parse_longitude(self):
        self.assertAlmostEqual(gps._parse_longitude('00924.41358', 'E'),
                               9.406893, 4)
        self.assertAlmostEqual(gps._parse_longitude('00924.41358', 'W'),
                               -9.406893, 4)
        self.assertRaises(ValueError, gps._parse_longitude, '3855.23816', 'X')

    def test_parse_quality(self):
        self.assertEqual(gps._parse_quality('0'), 'no_fix')
        self.assertEqual(gps._parse_quality('1'), 'gps')
        self.assertEqual(gps._parse_quality('2'), 'dgps')
        self.assertRaises(IndexError, gps._parse_quality, '4')
        self.assertRaises(ValueError, gps._parse_quality, 'lol1337')

    def test_parse_fix_type(self):
        self.assertEqual(gps._parse_fix_type('1'), 'no_fix')
        self.assertEqual(gps._parse_fix_type('2'), '2d')
        self.assertEqual(gps._parse_fix_type('3'), '3d')
        self.assertRaises(IndexError, gps._parse_quality, '4')
        self.assertRaises(ValueError, gps._parse_quality, 'lol1337')

    def test_parse_speed(self):
        self.assertAlmostEqual(gps._parse_speed('31.332'), 58.026864, 3)
        self.assertRaises(ValueError, gps._parse_speed, 'lol1337')

    def test_checksum_valid(self):
        self.assertEqual(gps._checksum_valid(
            '$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39'), True)
        self.assertEqual(gps._checksum_valid(
            '$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48'), True)
        self.assertEqual(gps._checksum_valid(
            '$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*4'), False)
        self.assertEqual(gps._checksum_valid(
            '$GPGSA,B,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39'), False)
        self.assertRaises(ValueError, gps._checksum_valid, 'random')
        self.assertRaises(ValueError, gps._checksum_valid, '$lol')
        self.assertRaises(ValueError, gps._checksum_valid, 'lol*')
