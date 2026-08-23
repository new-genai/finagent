import uuid
from pathlib import Path
from typing import Any, List

from .interfaces import Parser
from .models import FinancialReport, Page, Table, Metadata
from .exceptions import ParserError

# Import all modules
from .txt_reader import TXTReader
from .metadata_extractor import MetadataExtractor
from .page_splitter import PageSplitter
from .table_detector import TableDetector
from .table_extractor import TableExtractor

class FinancialReportParser(Parser):
    """
    Concrete Builder for parsing financial reports.
    Implements a Fluent Interface for method chaining.
    """

    def __init__(self) -> None:
        # Khởi tạo toàn bộ các module (Sub-components)
        self.txt_reader = TXTReader()
        self.metadata_extractor = MetadataExtractor()
        self.page_splitter = PageSplitter()
        self.table_detector = TableDetector()
        self.table_extractor = TableExtractor()
        
        # State khởi tạo
        self.reset()

    def reset(self) -> None:
        """Resets the internal state to start a new parsing process."""
        self._file_path = None
        self._raw_text = None
        self._pages = []
        self._metadata = None
        self._temp_table_locations = {}

    def parse(self, file_path: Path | str) -> FinancialReport:
        """Main entry point required by Parser Interface."""
        # Gọi Builder theo đúng Fluent Interface
        return (
            self.read(file_path)
                .extract_metadata()
                .split_pages()
                .detect_tables()
                .extract_tables()
                .build()
        )

    def read(self, path: Path | str) -> 'FinancialReportParser':
        """Reads the raw file content and initializes state."""
        self.reset()
        self._file_path = Path(path)
        self._raw_text = self.txt_reader.read(self._file_path)
        return self

    def split_pages(self) -> 'FinancialReportParser':
        """Splits the content into logical pages."""
        if self._raw_text is None:
            raise ParserError("Must call read() before split_pages().")
            
        self._pages = self.page_splitter.split_pages(self._raw_text)
        return self

    def detect_tables(self) -> 'FinancialReportParser':
        """Detects tables within each page."""
        if not self._pages:
            raise ParserError("Must call split_pages() before detect_tables().")
            
        for page in self._pages:
            locations = self.table_detector.detect(page.content)
            self._temp_table_locations[page.page_number] = locations
        return self

    def extract_tables(self) -> 'FinancialReportParser':
        """Extracts table data into Table models for each page and merges split tables."""
        if not self._temp_table_locations and not self._pages:
            raise ParserError("Must call detect_tables() before extract_tables().")
            
        for page in self._pages:
            locations = self._temp_table_locations.get(page.page_number, [])
            page.tables = []
            for loc in locations:
                table = self.table_extractor.extract(page.content, loc, page_number=page.page_number)
                page.tables.append(table)
                
        # --- BẮT ĐẦU SPATIAL MERGING (GỘP BẢNG VẮT TRANG) ---
        for i in range(1, len(self._pages)):
            prev_page = self._pages[i-1]
            curr_page = self._pages[i]
            
            if prev_page.tables and curr_page.tables:
                last_table_prev = prev_page.tables[-1]
                first_table_curr = curr_page.tables[0]
                
                # Nhận diện Spatial: Nếu 2 bảng có cùng Header, tức là cùng 1 bảng bị cắt trang
                if last_table_prev.headers and first_table_curr.headers:
                    if last_table_prev.headers == first_table_curr.headers:
                        # Nối Rows của Child vào Parent Table
                        last_table_prev.rows.extend(first_table_curr.rows)
                        # Xóa bảng mảnh vỡ ở trang hiện tại
                        curr_page.tables.pop(0)
        # --- KẾT THÚC SPATIAL MERGING ---
        
        return self

    def extract_metadata(self) -> 'FinancialReportParser':
        """Extracts document metadata."""
        if self._file_path is None:
            raise ParserError("Must call read() before extract_metadata().")
            
        self._metadata = self.metadata_extractor.extract(str(self._file_path))
        return self

    def build(self) -> FinancialReport:
        """Builds and returns the final FinancialReport object."""
        if self._metadata is None:
            self._metadata = Metadata()
            
        if not self._pages:
            raise ParserError("Cannot build report without parsing pages first.")
            
        return FinancialReport(
            report_id=str(uuid.uuid4()),
            metadata=self._metadata,
            pages=self._pages,
            raw_content=self._raw_text
        )
