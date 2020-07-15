import logging , os
from pathlib import Path

def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("bluicity")
    logger.setLevel(logging.DEBUG)
    file = os.path.expanduser('~/logs.log')
    # create the logging file handler
    fh = logging.FileHandler(filename=Path(file))
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    return logger
logger = create_logger()