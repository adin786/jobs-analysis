import logging


levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
}


def make_logger(name: str, level: str, add_handler: bool = False):
    logger = logging.getLogger(name)
    logger.setLevel(levels[level])
    
    if add_handler:
        formatter = logging.Formatter(fmt="%(levelname)s:%(name)s:%(message)s ")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger