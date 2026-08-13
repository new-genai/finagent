import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.parser import FinancialReportParser
from src.parser.models import FinancialReport

logger = logging.getLogger(__name__)

class MetadataBuilder:
    """Scans dataset and generates metadata.parquet."""
    
    def __init__(self):
        self.parser = FinancialReportParser()
        
    def build_metadata(self, data_dir: Path, output_path: Path) -> pd.DataFrame:
        """
        Quét toàn bộ dataset, sinh metadata tổng quan.
        Bao gồm: company, ticker, year, report, table_count, csv_path, duckdb_table
        """
        logger.info(f"Building metadata from {data_dir}")
        
        records = []
        txt_files = list(data_dir.glob("*.txt"))
        if not txt_files:
            logger.warning(f"No txt files found in {data_dir}")
            
        for file_path in txt_files:
            try:
                # Dùng parser để bóc tách thông tin
                report = self.parser.parse(file_path)
                meta = report.metadata.additional_info
                
                ticker = meta.get("ticker", "UNKNOWN")
                year = meta.get("year", "YYYY")
                report_type = meta.get("report_type", "UNKNOWN")
                
                table_count = sum(len(page.tables) for page in report.pages)
                
                records.append({
                    "company": ticker,
                    "ticker": ticker,
                    "year": year,
                    "report": report_type,
                    "table_count": table_count,
                    "source_file": file_path.name
                })
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                
        # Nếu chưa có file nào, tạo dummy dataframe để tránh lỗi
        if not records:
            df = pd.DataFrame(columns=["company", "ticker", "year", "report", "table_count", "source_file"])
        else:
            df = pd.DataFrame(records)
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        logger.info(f"Saved metadata to {output_path}")
        return df

class SchemaBuilder:
    """Generates schema metadata for each table (title, headers, keywords)."""
    
    def build_schema(self, report: FinancialReport) -> List[Dict[str, Any]]:
        """
        Sinh metadata cho từng table.
        title, headers, keywords, year, company, table_id
        """
        schemas = []
        meta = report.metadata.additional_info
        ticker = meta.get("ticker", "UNKNOWN")
        year = meta.get("year", "YYYY")
        
        for page in report.pages:
            for i, table in enumerate(page.tables, 1):
                # Basic keywords extraction (e.g. từ headers và một phần nội dung rows)
                keywords = [str(h).lower() for h in table.headers] if table.headers else []
                if table.rows:
                    for row in table.rows:
                        keywords.extend([str(c).lower() for c in row if c])
                
                schema = {
                    "table_id": table.id,
                    "company": ticker,
                    "year": year,
                    "title": f"Table {i} - Page {page.page_number} of {ticker} {year}",
                    "headers": table.headers,
                    "keywords": keywords,
                    "duckdb_table": f"{ticker}_{year}_page{page.page_number}_table{i}"
                }
                schemas.append(schema)
                
        return schemas
