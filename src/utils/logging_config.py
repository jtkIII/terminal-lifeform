"""
File: logging_config.py
Author: Jtk III
Date: 2024-06-10
Description: Logging configuration for the simulation.
"""

import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # goes up from src/ to project root
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)  # ensure logs/ exists
LOG_FILE = LOGS_DIR / "simulation.log"


def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(
        logging.INFO
    )  # Set to logging.DEBUG to see detailed interaction logs

    # Use mode="w" to overwrite the log file each run
    file_handler = logging.FileHandler(LOG_FILE, mode="w")
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# filepath: /home/jtk/Dev/TerminalLifeform/src/utils/logging_config.py
