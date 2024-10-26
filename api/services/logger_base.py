# services/logger_base.py

import logging
import os

# Read the DEBUG flag from environment variables
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')


def setup_logging():
    if len(logging.root.handlers) == 0:
        log_level = logging.DEBUG if DEBUG else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            # Uncomment the following line to log to a file
            # filename='app.log',
        )
        # Optionally, add a file handler
        # file_handler = logging.FileHandler('app.log')
        # file_handler.setLevel(log_level)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # file_handler.setFormatter(formatter)
        # logging.getLogger('').addHandler(file_handler)


# Automatically configure logging when the module is imported
setup_logging()