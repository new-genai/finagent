import re
import logging
from pathlib import Path

from .models import Metadata
from .utils import setup_logger

logger = setup_logger(__name__)

class MetadataExtractor:
    """Extractor for parsing metadata from filenames using regex."""
    
    def __init__(self) -> None:
        # Regex giải thích:
        # ^([A-Za-z0-9]+)_     : Group 1 (Ticker) - Bắt đầu chuỗi, lấy các chữ cái/số, kết thúc bằng dấu '_'
        # (?:.*?_)?            : Non-capturing group - Lấy các ký tự ở giữa (ví dụ 'financial_statements_'), có hoặc không cũng được (dấu ? ở cuối), sử dụng .*? để match non-greedy (lấy ít nhất có thể) cho đến khi gặp '_'
        # (\d{4})_             : Group 2 (Year) - Chính xác 4 chữ số, theo sau là dấu '_'
        # ([A-Za-z0-9_]+)      : Group 3 (Report Type) - Lấy chữ cái, số, và dấu '_' (ví dụ 'consolidated' hoặc 'q1_review')
        # (?:\.[a-zA-Z0-9]+)?$ : Non-capturing group - Đuôi file (ví dụ '.txt'), có hoặc không, và kết thúc chuỗi ($)
        self.pattern = re.compile(
            r'^([A-Za-z0-9]+)_(?:.*?_)?(\d{4})_([A-Za-z0-9_]+)(?:\.[a-zA-Z0-9]+)?$'
        )

    def extract(self, filename: str) -> Metadata:
        """
        Extracts ticker, year, and report_type from a filename.
        Returns a Metadata object.
        """
        # Nếu input là đường dẫn dài (path), chỉ lấy tên file để phân tích
        name_only = Path(filename).name
        logger.debug(f"Extracting metadata from: {name_only}")
        
        # Lưu name_only vào thuộc tính source của Metadata
        metadata = Metadata(source=name_only)
        
        match = self.pattern.search(name_only)
        
        if match:
            ticker = match.group(1).upper()
            year = match.group(2)
            report_type = match.group(3).lower()
            
            logger.info(f"Successfully matched: Ticker={ticker}, Year={year}, Type={report_type}")
            
            # Lưu các thông tin extract được vào additional_info vì không muốn can thiệp sửa models.py
            metadata.additional_info = {
                "ticker": ticker,
                "year": year,
                "report_type": report_type,
                "filename": name_only
            }
        else:
            logger.warning(f"Filename does not match expected metadata pattern: {name_only}")
            metadata.additional_info = {
                "filename": name_only
            }
            
        return metadata
