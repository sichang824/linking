import logging

LOGGER_FMT = '%(asctime)s %(message)s'
LOGGER_DATE_FMT = '%Y-%m-%d %H:%M:%S'
LOGGER_LEVEL = logging.INFO
LOGGER_NAME = "msync"

if LOGGER_LEVEL == logging.DEBUG:
    LOGGER_FMT = '%(asctime)s %(levelname)s [%(lineno)d:%(filename)s:%(name)s] %(message)s'

# logging.basicConfig(filename="/Users/sichang/log/msync.collect.log",
#                     filemode='a',
#                     level=LOGGER_LEVEL,
#                     format=LOGGER_FMT,
#                     datefmt=LOGGER_DATE_FMT)
logging.basicConfig(level=LOGGER_LEVEL,
                    format=LOGGER_FMT,
                    datefmt=LOGGER_DATE_FMT)
logger = logging.getLogger(LOGGER_NAME)
