from time import sleep
import traceback

from tsparser import main
from tsparser.ui import UserInterface
from tsparser.utils.statistic_data_collector import StatisticDataCollector

UserInterface().run()
try:
    main.parse()
except Exception:
    logger = StatisticDataCollector().get_logger()
    logger.log('system', traceback.format_exc())
    logger.log('system', 'System has crashed. Please exit manually.')
    while True:
        sleep(1)
