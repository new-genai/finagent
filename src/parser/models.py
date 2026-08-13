from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Metadata:
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None
    source: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Table:
    id: str
    page_number: int
    headers: List[str]
    rows: List[List[Any]]
    caption: Optional[str] = None

@dataclass
class Page:
    page_number: int
    content: str
    tables: List[Table] = field(default_factory=list)

@dataclass
class FinancialReport:
    report_id: str
    metadata: Metadata
    pages: List[Page] = field(default_factory=list)
    raw_content: Optional[str] = None
