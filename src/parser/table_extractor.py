import re
import uuid
import logging
from typing import Tuple, List
from html.parser import HTMLParser
import pandas as pd
from .models import Table
from .utils import setup_logger

logger = setup_logger(__name__)

class _HTMLTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows: List[List[str]] = []
        self.current_row: List[str] = []
        self.current_cell: List[str] = []
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = []
        elif tag == 'tr':
            self.current_row = []

    def handle_endtag(self, tag):
        if tag in ('td', 'th'):
            if self.in_cell:
                self.current_row.append("".join(self.current_cell).strip())
                self.in_cell = False
        elif tag == 'tr':
            if self.current_row:
                self.rows.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

class TableExtractor:
    """Trích xuất khối bảng từ raw text với cấu trúc nguyên vẹn 100%."""
    def __init__(self) -> None:
        pass

    def _clean_parsed_rows(self, parsed_data: List[List[str]]) -> List[List[str]]:
        if not parsed_data:
            return []
            
        header_row = [str(c).strip() for c in parsed_data[0]]
        # Forward fill cho header bị merge
        for i in range(1, len(header_row)):
            if not header_row[i] and header_row[i - 1]:
                header_row[i] = header_row[i - 1]
                
        cleaned_data: List[List[str]] = [header_row]
        
        # Giữ nguyên bản toàn bộ dòng dữ liệu, chỉ căn chỉnh độ dài bằng header
        for row in parsed_data[1:]:
            row_clean = [str(c).strip() for c in row]
            while len(row_clean) < len(header_row):
                row_clean.append("")
            cleaned_data.append(row_clean[:len(header_row)])
            
        return cleaned_data

    def extract(self, text: str, location: Tuple[int, int], page_number: int = 1) -> Table:
        start, end = location
        table_block = text[start:end].strip()
        
        if not table_block:
            return Table(id=str(uuid.uuid4()), page_number=page_number, headers=[], rows=[])
            
        parsed_data: List[List[str]] = []
        
        if '<table' in table_block.lower() and '</table>' in table_block.lower():
            html_parser = _HTMLTableParser()
            html_parser.feed(table_block)
            parsed_data = html_parser.rows
        else:
            lines = table_block.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if '|' in line:
                    if re.match(r'^[\s\|\-]+$', line):
                        continue
                    row = [col.strip() for col in line.split('|')]
                    if row and not row[0]: row = row[1:]
                    if row and not row[-1]: row = row[:-1]
                    parsed_data.append(row)
                else:
                    row = re.split(r'[ \t]{2,}', line)
                    parsed_data.append([col.strip() for col in row if col.strip()])
                    
        if parsed_data:
            parsed_data = self._clean_parsed_rows(parsed_data)
            
        headers = parsed_data[0] if parsed_data else []
        raw_rows = parsed_data[1:] if len(parsed_data) > 1 else []
        
        # Lưu toàn bộ dữ liệu dưới dạng Text nguyên gốc để không bị mất chữ
        clean_rows = [[str(cell).strip() for cell in row] for row in raw_rows]
        table_id = str(uuid.uuid4())
        
        return Table(id=table_id, page_number=page_number, headers=headers, rows=clean_rows)