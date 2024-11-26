import logging
import os
from datetime import datetime

LOGS_DIR = "logs/dailyLogs"
DAILY_LOG_FILE = os.path.join(LOGS_DIR, f"daily_log_{datetime.utcnow().date()}.log")

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

def setupLogger():
    """Setup logger with file and console handlers."""
    logger = logging.getLogger("NautilusBot")
    logger.setLevel(logging.INFO)

    # File handler
    fileHandler = logging.FileHandler(DAILY_LOG_FILE)
    fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    return logger

logger = setupLogger()
