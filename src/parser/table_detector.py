import re
import logging
from typing import List, Tuple
from .utils import setup_logger

logger = setup_logger(__name__)

class TableDetector:
    """Tự động phát hiện vị trí cả bảng HTML (<table>) và bảng Markdown (|)."""
    
    def __init__(self) -> None:
        self.html_pattern = re.compile(
            r"<table.*?>.*?</table>",
            re.MULTILINE | re.IGNORECASE | re.DOTALL
        )
        # Regex bắt các khối bảng Markdown có từ 2 dòng chứa dấu gạch đứng | trở lên
        self.markdown_pattern = re.compile(
            r"((?:^[ \t]*\|.+?\|[ \t]*\r?\n){2,})",
            re.MULTILINE
        )

    def detect(self, text: str) -> List[Tuple[int, int]]:
        if not text:
            return []
            
        locations = []
        
        # 1. Quét bảng HTML
        for match in self.html_pattern.finditer(text):
            locations.append(match.span())
            
        # 2. Quét bảng Markdown
        for match in self.markdown_pattern.finditer(text):
            span = match.span()
            # Tránh trùng lặp nếu nằm trong khối HTML
            if not any(loc[0] <= span[0] and span[1] <= loc[1] for loc in locations):
                locations.append(span)
                
        locations.sort(key=lambda x: x[0])
        logger.info(f"Phát hiện {len(locations)} bảng trong tài liệu.")
        return locations