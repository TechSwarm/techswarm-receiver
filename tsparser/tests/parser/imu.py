from tsparser.parser import imu
from tsparser.tests.parser import ParserTestCase, DEFAULT_TIMESTAMP


class TestIMU(ParserTestCase):
    ex_data = {'timestamp': DEFAULT_TIMESTAMP, 'pressure': 3981106,
               'gyro_x': -413, 'gyro_y': -1286, 'gyro_z': -2545,
               'accel_x': 14400, 'accel_y': 3328, 'accel_z': 5440,
               'magnet_x': 13310, 'magnet_y': -32001, 'magnet_z': 5118}
    lines = ['$GYRO,-413,-1286,-2545', '$ACCEL,14400,3328,5440',
             '$MAGNET,13310,-32001,5118', '$MBAR,3981106']

    def test_imu_parser(self):
        """Test IMUParser with standard output"""
        for line in self.lines[:3]:
            self.parse_line(line)
        self.assertEqual(self.send_data_mock.called, False)
        self.parse_line(self.lines[3])
        self.send_data_mock.assert_called_with(self.ex_data, imu.IMUParser.url)

    def test_imu_parser_different_order(self):
        """Test IMUParser with input in different order"""
        self.parse_line(self.lines[1])
        self.parse_line(self.lines[3])
        self.parse_line(self.lines[2])
        self.assertEqual(self.send_data_mock.called, False)
        self.parse_line(self.lines[0])
        self.send_data_mock.assert_called_with(self.ex_data, imu.IMUParser.url)

    def test_imu_parser_invalid_data(self):
        """Test IMUParser with invalid input"""
        self.assertRaises(ValueError, self.parse_line, '$GYRO,111')
        self.assertRaises(ValueError, self.parse_line, '$GYRO,a,b,c')
        self.assertRaises(ValueError, self.parse_line, '$ACCEL,111,-1,222,4')
        self.assertRaises(ValueError, self.parse_line, '$MAGNET,82,222')
        self.assertRaises(ValueError, self.parse_line, '$MBAR,1,2')
