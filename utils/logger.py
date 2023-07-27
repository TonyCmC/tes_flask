import logging
from datetime import datetime
from config import *


class Logger:
    def __init__(self, suffix='all'):
        today = datetime.today().strftime('%Y-%m-%d')
        self._logger = logging.getLogger(suffix)
        file_handler = logging.FileHandler(f'{ROOT_DIR}/logs/{today}-{suffix}.log')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        file_handler.setLevel(logging.INFO)
        self._logger.addHandler(file_handler)

    @property
    def logger(self):
        return self._logger
