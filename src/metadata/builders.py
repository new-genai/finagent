import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from src.parser.models import FinancialReport

logger = logging.getLogger(__name__)

class MetadataBuilder:
    def __init__(self):
        from src.parser.report_parser import FinancialReportParser
        self.parser = FinancialReportParser()

    def build_metadata(self, data_dir: Path, output_path: Path) -> pd.DataFrame:
        records = []
        for file_path in list(data_dir.glob("*.txt")):
            try:
                report = self.parser.parse(file_path)
                meta = report.metadata.additional_info
                records.append({
                    "company": meta.get("ticker", "UNKNOWN"),
                    "ticker": meta.get("ticker", "UNKNOWN"),
                    "year": meta.get("year", "YYYY"),
                    "report": meta.get("report_type", "UNKNOWN"),
                    "table_count": sum(len(page.tables) for page in report.pages),
                    "source_file": file_path.name
                })
            except Exception as e:
                logger.error(f"Lỗi: {e}")
        df = pd.DataFrame(records)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        return df

class SchemaBuilder:
    def _categorize_table(self, headers: List[str], keywords: List[str]) -> str:
        content = " ".join(headers + keywords).lower()
        if "kết quả" in content or "doanh thu" in content or "lợi nhuận" in content:
            return "BÁO CÁO KẾT QUẢ KINH DOANH"
        if "cân đối" in content or "tài sản" in content or "nguồn vốn" in content:
            return "BẢNG CÂN ĐỐI KẾ TOÁN"
        if "lưu chuyển" in content or "tiền tệ" in content:
            return "BÁO CÁO LƯU CHUYỂN TIỀN TỆ"
        return "THUYẾT MINH"

    def build_schema(self, report: FinancialReport) -> List[Dict[str, Any]]:
        schemas = []
        meta = report.metadata.additional_info
        ticker = meta.get("ticker", "UNKNOWN").upper().strip()
        year = str(meta.get("year", "YYYY")).strip()
        
        source_name = str(meta.get("filename", "")).lower()
        if "separate" in source_name or "rieng" in source_name:
            report_type = "separate"
        else:
            report_type = "consolidated"
            
        for page in report.pages:
            for i, table in enumerate(page.tables, 1):
                row_indicators = []
                if table.rows:
                    for row in table.rows:
                        if row and len(row) > 0 and str(row[0]).strip():
                            val = str(row[0]).strip()
                            if not val.replace('.', '').replace(',', '').isdigit():
                                row_indicators.append(val)
                                
                category = self._categorize_table(table.headers, row_indicators)
                duckdb_table = f"{ticker}_{year}_page{page.page_number}_table{i}"
                table_id = table.id if getattr(table, "id", None) else duckdb_table
                
                schema = {
                    "table_id": table_id,
                    "duckdb_table": duckdb_table,
                    "company": ticker,
                    "year": year,
                    "report_type": report_type,
                    "table_category": category,
                    "title": f"[{ticker} {year} {report_type.upper()}] {category} - Trang {page.page_number} Bảng {i}",
                    "headers": table.headers if table.headers else [],
                    "keywords": row_indicators  # <--- ĐÃ GỠ BỎ GIỚI HẠN [:30] DO BẠN PHÁT HIỆN
                }
                schemas.append(schema)
        return schemas
