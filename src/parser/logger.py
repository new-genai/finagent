"""
Logger setup for the Dataset Parser module.
"""
import logging

def get_logger(name: str = "dataset_parser") -> logging.Logger:
    """Returns a configured logger for the parser module."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
