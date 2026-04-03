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
    
    # Avoid adding multiple handlers if setup is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 1. File Handler for detailed logging
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s'
    )
    file_handler = logging.FileHandler('trading_bot.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # 2. Add Handlers to the Logger
    logger.addHandler(file_handler)

    # Explicitly do not add stream handler here since we use rich for console output in CLI
    # Only exception is if we wanted non-rich raw dumps to terminal, but CLI layer handles its own UX.
    
    return logger

