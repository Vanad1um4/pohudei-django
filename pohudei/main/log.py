import logging


def get_logger(
        LOG_FORMAT='[%(asctime)s] :: [%(name)s] :: [%(levelname)s] :: [FROM DEF %(funcName)s] :: [%(message)s]',
        LOG_NAME='',
        LOG_FILE_DEBUG='logs/debug.log',
        LOG_FILE_CRITICAL='logs/exceptions.log'):

    logger = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)

    # comment this to suppress console output
    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(log_formatter)
    # logger.addHandler(stream_handler)

    file_handler_info = logging.FileHandler(LOG_FILE_DEBUG, mode='a')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.DEBUG)
    logger.addHandler(file_handler_info)

    file_handler_error = logging.FileHandler(LOG_FILE_CRITICAL, mode='a')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.CRITICAL)
    logger.addHandler(file_handler_error)

    logger.setLevel(logging.DEBUG)

    return logger
