import logging , os , sys
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
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler) #fh
    return logger
logger = create_logger()