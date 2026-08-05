"""
Data models for the Dataset Parser module.
"""
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class ReportMetadata:
    """Metadata extracted from the financial report path or structure."""
    company: str
    year: int
    report_type: str
    report_name: str
    file_size: int
    language: str = "vi"
    encoding: str = "utf-8"

@dataclass
class ReportStatistics:
    """Statistics about the financial report content."""
    character_count: int = 0
    line_count: int = 0
    page_count: int = 0
    table_count: int = 0

@dataclass
class Page:
    """Placeholder for a page extracted from the report (Sprint 2)."""
    page_number: int
    content: str

@dataclass
class Table:
    """Placeholder for a table extracted from the report (Sprint 2)."""
    table_id: str
    title: str
    page: int
    content: str

@dataclass
class FinancialReport:
    """The central object representing a parsed financial report."""
    report_id: str
    company: str
    year: int
    report_type: str
    file_name: str
    source_path: str
    encoding: str
    metadata: ReportMetadata
    statistics: ReportStatistics
    raw_text: str
    pages: List[Page] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> str:
        """Serialize the FinancialReport object to a JSON string."""
        from dataclasses import asdict
        data = asdict(self)
        return json.dumps(data, ensure_ascii=False, indent=2)
