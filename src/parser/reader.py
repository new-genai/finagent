"""
Text Reader module for the Dataset Parser.
"""
from pathlib import Path
from typing import Tuple

from .exceptions import DatasetNotFoundError, EncodingError
from .config import ParserConfig
from .logger import get_logger

logger = get_logger("dataset_parser.reader")

class TXTReader:
    """Reads raw TXT files and handles encoding."""

    def __init__(self, config: ParserConfig):
        self.config = config

    def read(self, file_path: str | Path) -> Tuple[str, str]:
        """
        Read a text file and return its content and the encoding used.

        Args:
            file_path: Path to the text file.

        Returns:
            Tuple[str, str]: The file content and the encoding used.

        Raises:
            DatasetNotFoundError: If the file does not exist.
            EncodingError: If the file cannot be decoded.
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {path}")
            raise DatasetNotFoundError(f"File not found: {path}")
            
        if not path.is_file():
            logger.error(f"Not a file: {path}")
            raise DatasetNotFoundError(f"Not a file: {path}")

        encodings_to_try = [self.config.default_encoding, self.config.fallback_encoding]

        for enc in encodings_to_try:
            try:
                with open(path, "r", encoding=enc) as f:
                    content = f.read()
                logger.info(f"Successfully read {path.name} using {enc} encoding.")
                return content, enc
            except UnicodeDecodeError:
                logger.debug(f"Failed to read {path.name} with encoding {enc}.")
                continue
            except Exception as e:
                logger.error(f"Unexpected error reading {path.name}: {e}")
                raise

        logger.error(f"Failed to decode {path.name} with any configured encoding.")
        raise EncodingError(f"Cannot decode {path.name} with provided encodings.")
