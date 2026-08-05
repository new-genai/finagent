"""
Main parser module acting as the Facade.
"""
import hashlib
from pathlib import Path

from .config import ParserConfig
from .reader import TXTReader
from .metadata import MetadataExtractor
from .models import FinancialReport, ReportStatistics
from .exceptions import InvalidReportError
from .logger import get_logger

logger = get_logger("dataset_parser.parser")

class FinancialReportParser:
    """
    The main Facade for parsing financial reports.
    Executes the internal pipeline and returns a FinancialReport object.
    """

    def __init__(self, config: ParserConfig = None):
        self.config = config or ParserConfig()
        self.reader = TXTReader(self.config)
        self.metadata_extractor = MetadataExtractor()

    def _generate_id(self, content: str, file_path: Path) -> str:
        """Generate a unique ID for the report."""
        unique_string = f"{file_path.name}_{len(content)}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

    def _generate_statistics(self, content: str) -> ReportStatistics:
        """Generate simple statistics from the raw text."""
        char_count = len(content)
        line_count = len(content.splitlines())
        
        # In Sprint 1, table and page counts are placeholders (0)
        # We can implement simple heuristic for table_count just to show stats
        table_count = content.count("<table>")
        
        return ReportStatistics(
            character_count=char_count,
            line_count=line_count,
            page_count=0,  # Sprint 2
            table_count=table_count
        )

    def parse(self, file_path: str | Path) -> FinancialReport:
        """
        Parse a financial report file and build a FinancialReport object.
        
        Args:
            file_path: Path to the financial report file.
            
        Returns:
            FinancialReport: The fully constructed report object.
            
        Raises:
            ParserError: Various subclass errors if parsing fails.
        """
        path = Path(file_path)
        logger.info(f"Starting parsing for {path.name}")

        # Step 1: Read raw text
        raw_text, encoding = self.reader.read(path)
        if not raw_text.strip() and self.config.strict_mode:
            raise InvalidReportError(f"Report {path.name} is empty.")

        # Step 2: Extract metadata
        metadata = self.metadata_extractor.extract(path)
        metadata.encoding = encoding

        # Step 3: Generate statistics
        statistics = self._generate_statistics(raw_text)

        # Step 4: Build FinancialReport
        report_id = self._generate_id(raw_text, path)
        
        report = FinancialReport(
            report_id=report_id,
            company=metadata.company,
            year=metadata.year,
            report_type=metadata.report_type,
            file_name=path.name,
            source_path=str(path.absolute()),
            encoding=encoding,
            metadata=metadata,
            statistics=statistics,
            raw_text=raw_text,
            pages=[],  # Will be populated in Sprint 2
            tables=[]  # Will be populated in Sprint 2
        )

        logger.info(f"Successfully parsed report: {metadata.company} {metadata.year}")
        return report
