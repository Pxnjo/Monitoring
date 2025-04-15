import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Scrive sul file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Mostra anche a schermo
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Aggiunge gli handler solo se non già presenti
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger