import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """
    Sets up logging to both a file and standard output stream.
    File logs contain detailed debug information.
    Console logs are kept at basic INFO level mostly for non-interactive messages.
    """
    
    logger = logging.getLogger('trading_bot')
    
 
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)


    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s'
    )
    file_handler = logging.FileHandler('trading_bot.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)


    logger.addHandler(file_handler)

  
    
    return logger

