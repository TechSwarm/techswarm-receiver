from time import sleep

from tsparser import main
from tsparser.ui import UserInterface
from tsparser.utils.statistic_data_collector import StatisticDataCollector

UserInterface().run()
try:
    main.parse()
except Exception as err:
    logger = StatisticDataCollector().get_logger()
    logger.log('system', '{}: {}'.format(err.__class__.__name__, err))
    logger.log('system', 'System has crashed. Please exit manually.')
    while True:
        sleep(1)
