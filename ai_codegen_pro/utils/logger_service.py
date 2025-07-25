from ai_codegen_pro.utils.logger_service import log
import sys

def setup_logger(name="ai_codegen", level=log.INFO):
    logger = log.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = log.StreamHandler(sys.stdout)
        formatter = log.Formatter('[%(levelname)s] %(asctime)s - %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

# Shortcut für globalen Logger
log = setup_logger()
