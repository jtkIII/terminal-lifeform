import logging


def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(
        logging.INFO
    )  # Set to logging.DEBUG to see detailed interaction logs

    file_handler = logging.FileHandler("logs/simulation.log", mode="w")
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
