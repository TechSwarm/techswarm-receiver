from copy import deepcopy
import functools
import math
import operator
from threading import Thread, Lock
from time import sleep
import traceback

from tsparser import config, sender
from tsparser.timestamp import get_timestamp
from tsparser.utils.singleton import Singleton
from tsparser.utils.statistic_data_collector import StatisticDataCollector


# physical constants

G = 6.67384e-11


class Calculator(metaclass=Singleton):
    url = config.URL + '/planetarydata'

    def __init__(self):
        self.__DATA_BUFFER_SCHEME = {
            'gps': list(),
            'imu': list(),
            'sht': list()
        }
        self.__new_data_buffer = deepcopy(self.__DATA_BUFFER_SCHEME)
        self.__all_data = deepcopy(self.__DATA_BUFFER_SCHEME)
        self.__data_frame = deepcopy(self.__DATA_BUFFER_SCHEME)
        self.__data_mutex = Lock()
        self.__calculated_data = dict()
        self.__accel_and_alt_cache = list()  # acceleration and altitude
        Thread(target=self.__calculator_thread, daemon=True).start()

    def on_data_update(self, source, data):
        if not self.__check_data_packet_validity(source, data):
            return
        self.__data_mutex.acquire()
        self.__data_frame[source] = data
        if all(self.__data_frame.values()):
            for k, v in self.__data_frame.items():
                self.__new_data_buffer[k].append(v)
            self.__data_frame = deepcopy(self.__DATA_BUFFER_SCHEME)
        self.__data_mutex.release()

    @staticmethod
    def __check_data_packet_validity(source, data):
        if source == 'gps':
            if 'altitude' not in data:
                return False
        return True

    def __calculator_thread(self):
        try:
            self.__calculator_loop()
        except Exception:
            StatisticDataCollector().get_logger().log('esi_calculator',
                                                      traceback.format_exc())

    def __calculator_loop(self):
        while True:
            self.__data_mutex.acquire()
            if all(self.__new_data_buffer.values()):
                self.__calculated_data['timestamp'] = get_timestamp()
                for key in self.__DATA_BUFFER_SCHEME.keys():
                    self.__all_data[key].extend(self.__new_data_buffer[key])
                self.__new_data_buffer = deepcopy(self.__DATA_BUFFER_SCHEME)
                self.__data_mutex.release()
                # Do *NOT* block on_data_update method!

                self.__calculate_data()
                sender.send_data(self.__calculated_data, self.url)

            if self.__data_mutex.locked():
                self.__data_mutex.release()
            sleep(0.01)

    def __calculate_data(self):
        self.__cache_accel_and_alt()
        self.__calculate_mass_and_radius()
        self.__calculate_earth_density()
        self.__calculate_escape_speed()
        self.__calculate_esi()

    def __cache_accel_and_alt(self):
        accel_factor = 0.061 / 1000
        begin_ind = len(self.__accel_and_alt_cache)
        for imu, gps in zip(self.__all_data['imu'][begin_ind:],
                            self.__all_data['gps'][begin_ind:]):
            acceleration = math.sqrt(imu['accel_x']**2 + imu['accel_y']**2 +
                                     imu['accel_z']**2) * accel_factor
            altitude = gps['altitude']
            self.__accel_and_alt_cache.append((acceleration, altitude))

    def __calculate_mass_and_radius(self):
        best = {
            'error': float('inf'),
            'mass': 0,
            'radius': 0
        }

        for radius in range(1, int(1e6+1)):
            numerator, denominator = 0, 0
            for acceleration, altitude in self.__accel_and_alt_cache:
                numerator += (G * acceleration) / (radius + altitude)**2
                denominator += G / (radius + altitude)**2
            mass = numerator / denominator**2

            error = 0
            for acceleration, altitude in self.__accel_and_alt_cache:
                error += (acceleration - G * mass / (radius + altitude)**2)**2

            if error < best['error']:
                best.update({
                    'error': error,
                    'mass': mass,
                    'radius': radius
                })

        self.__calculated_data.update({
            'radius': best['radius'],
            'mass': best['mass']
        })

    def __calculate_earth_density(self):
        mass = self.__calculated_data['mass']
        radius = self.__calculated_data['radius']
        self.__calculated_data['density'] = mass / (4/3 * math.pi * radius**3)

    def __calculate_escape_speed(self):
        mass = self.__calculated_data['mass']
        radius = self.__calculated_data['radius']
        self.__calculated_data['escape_speed'] = math.sqrt(2*G * mass / radius)

    def __calculate_esi(self):
        esi_data = (
            # format: our value, earth value, parameter weight
            (self.__calculated_data['radius'], 6.37841e6, 0.57),
            (self.__calculated_data['density'], 5514, 1.07),
            (self.__calculated_data['escape_speed'], 11186, 0.70),
            (self.__all_data['sht'][-1]['temperature'] + 273.15, 288, 5.58),
        )
        factors = [(1 - abs((d[0] - d[1]) / (d[0] + d[1])))
                   ** (d[2] / len(esi_data)) for d in esi_data]
        self.__calculated_data['esi'] = functools.reduce(operator.mul,
                                                         factors, 1)
