import logging

logger = logging.getLogger(__name__)

def setup_logger(name: str) -> logging.Logger:
    """Utility to setup basic logger."""
    return logging.getLogger(name)
