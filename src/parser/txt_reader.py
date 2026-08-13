from pathlib import Path
from typing import List

from .exceptions import EncodingError, DatasetNotFoundError
from .utils import setup_logger

logger = setup_logger(__name__)

class TXTReader:
    """Reader for extracting text from .txt files."""

    def __init__(self) -> None:
        # Danh sách các encoding được hỗ trợ, ưu tiên theo thứ tự
        self.supported_encodings: List[str] = ['utf-8-sig', 'utf-8', 'cp1258']

    def read(self, path: Path | str) -> str:
        """
        Reads a text file and automatically handles encodings.
        Raises:
            DatasetNotFoundError: If the file does not exist.
            EncodingError: If the file cannot be decoded.
        """
        file_path = Path(path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise DatasetNotFoundError(f"File does not exist: {file_path}")
            
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise DatasetNotFoundError(f"Path is not a file: {file_path}")

        # Thử lần lượt các encoding
        for enc in self.supported_encodings:
            try:
                logger.debug(f"Attempting to read {file_path.name} with encoding: {enc}")
                content = file_path.read_text(encoding=enc)
                logger.info(f"Successfully read {file_path.name} using {enc} encoding.")
                return content
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode {file_path.name} with {enc}")
                continue
                
        logger.error(f"Failed to decode {file_path.name} with all supported encodings: {self.supported_encodings}")
        raise EncodingError(f"Cannot decode file {file_path}. Tried: {self.supported_encodings}")
