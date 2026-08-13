import re
import logging
from typing import List, Tuple

from .utils import setup_logger

logger = setup_logger(__name__)

class TableDetector:
    """Detects table locations in raw text using Regular Expressions."""
    
    def __init__(self) -> None:
        self.table_pattern = re.compile(
            r"<table.*?>.*?</table>",
            re.MULTILINE | re.IGNORECASE | re.DOTALL
        )

    def detect(self, text: str) -> List[Tuple[int, int]]:
        """
        Quét qua raw text và trả về danh sách các vị trí (start_index, end_index)
        chứa table. Không thực hiện extract dữ liệu.
        """
        logger.debug(f"Starting table detection on text of length {len(text)}")
        locations = []
        
        if not text:
            return locations
            
        # finditer quét qua chuỗi và trả về các Match Object chứa toạ độ (span)
        for match in self.table_pattern.finditer(text):
            start, end = match.span()
            locations.append((start, end))
            logger.info(f"Detected table at index [{start}:{end}]")
            
        logger.debug(f"Total tables detected: {len(locations)}")
        return locations
