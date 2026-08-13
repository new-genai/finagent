import re
import uuid
import logging
from typing import Tuple

from .models import Table
from .utils import setup_logger

logger = setup_logger(__name__)

class TableExtractor:
    """Extracts a table block from raw text into a Table dataclass."""
    
    def __init__(self) -> None:
        pass
        
    def extract(self, text: str, location: Tuple[int, int], page_number: int = 1) -> Table:
        """
        Extracts table content from a specific location in the raw text 
        and parses it into a Table dataclass.
        """
        start, end = location
        logger.debug(f"Extracting table at location [{start}:{end}]")
        
        # 1. Trích xuất đúng khối text của table dựa vào location
        table_block = text[start:end].strip()
        
        if not table_block:
            logger.warning("Empty table block extracted.")
            return Table(id=str(uuid.uuid4()), page_number=page_number, headers=[], rows=[])
            
        # 2. Phân biệt loại bảng (HTML vs Text)
        parsed_data = []
        if '<table' in table_block.lower() and '</table>' in table_block.lower():
            # Sử dụng HTMLParser để parse HTML Table
            from html.parser import HTMLParser
            
            class HTMLTableParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.rows = []
                    self.current_row = []
                    self.current_cell = []
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
            
            html_parser = HTMLTableParser()
            html_parser.feed(table_block)
            parsed_data = html_parser.rows
        else:
            # 3. Phân tách bảng text thông thường thành các dòng
            lines = table_block.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Phân tách cột (Parse Columns)
                # Nếu là Markdown Table (có dấu Pipe |)
                if '|' in line:
                    # Bỏ qua dòng format header (ví dụ: |---|---|)
                    if re.match(r'^[\s\|\-]+$', line):
                        continue
                    
                    # Cắt bằng dấu | và strip khoảng trắng
                    row = [col.strip() for col in line.split('|')]
                    
                    # Xoá các cột rỗng ở đầu và cuối (do syntax | Col 1 | Col 2 |)
                    if row and not row[0]: 
                        row = row[1:]
                    if row and not row[-1]: 
                        row = row[:-1]
                    
                    parsed_data.append(row)
                
                # Nếu là Space-separated Table
                else:
                    # Cắt bằng Regex: 2 khoảng trắng trở lên hoặc tab
                    row = re.split(r'[ \t]{2,}', line)
                    parsed_data.append([col.strip() for col in row if col.strip()])
                
        # 4. Ánh xạ vào headers và rows
        headers = parsed_data[0] if parsed_data else []
        rows = parsed_data[1:] if len(parsed_data) > 1 else []
        
        table_id = str(uuid.uuid4())
        logger.info(f"Successfully extracted table {table_id}: {len(headers)} cols, {len(rows)} rows.")
        
        # 5. Khởi tạo và trả về Table dataclass
        return Table(
            id=table_id,
            page_number=page_number,
            headers=headers,
            rows=rows
        )
