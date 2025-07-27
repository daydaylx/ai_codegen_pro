import logging
import sys


def setup_logger(name="ai_codegen", level=logging.INFO, logfile=None):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if logfile:
            file_handler = logging.FileHandler(logfile, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    return logger


log = setup_logger()
