import csv
import logging
from pathlib import Path
from typing import List

from .interfaces import Exporter
from src.parser.models import FinancialReport

logger = logging.getLogger(__name__)

class CSVExporter(Exporter):
    """
    Concrete Exporter: Xuất các bảng (Tables) trong FinancialReport thành file CSV.
    Vì một báo cáo có nhiều bảng, Exporter này sẽ xuất mỗi bảng thành 1 file riêng biệt
    nằm trong thư mục output_dir.
    """
    
    def export(self, report: FinancialReport, output_dir: Path | str) -> List[Path]:
        """
        Hàm thực thi export. 
        Trả về danh sách các đường dẫn (Paths) của những file CSV vừa được tạo ra.
        """
        out_dir = Path(output_dir)
        
        # Tự động tạo thư mục nếu chưa tồn tại
        out_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        # Trích xuất metadata để tạo tên file đẹp (Ví dụ: VNM_2023)
        meta = report.metadata.additional_info
        ticker = meta.get("ticker", "UNKNOWN")
        year = meta.get("year", "YYYY")
        
        # Duyệt qua từng page và từng table
        for page in report.pages:
            for i, table in enumerate(page.tables, 1):
                # Naming Convention: TICKER_YEAR_page1_table1.csv
                filename = f"{ticker}_{year}_page{page.page_number}_table{i}.csv"
                file_path = out_dir / filename
                
                # Mở file với encoding utf-8-sig để Excel hiển thị đúng Tiếng Việt (có dấu)
                with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    
                    # Ghi dòng Headers
                    if table.headers:
                        writer.writerow(table.headers)
                        
                    # Ghi tất cả các Rows
                    for row in table.rows:
                        writer.writerow(row)
                        
                exported_files.append(file_path)
                logger.info(f"Exported table to: {file_path}")
                
        return exported_files
