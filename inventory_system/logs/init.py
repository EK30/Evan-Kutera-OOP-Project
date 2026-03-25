import logging
from pathlib import Path


LOG_FILE = Path(__file__).resolve().parent / "inventory.log"


def setup_logging():
    # Configure one shared file logger for the whole application.
    logger = logging.getLogger("inventory_system")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )

    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


def get_logger():
    return setup_logging()
