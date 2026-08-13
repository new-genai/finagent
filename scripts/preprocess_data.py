import os
import sys
import logging
from pathlib import Path
import csv
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure python can find src
sys.path.append(str(Path(__file__).parent.parent))

from src.parser import FinancialReportParser

def main():
    base_dir = Path(__file__).parent.parent
    raw_data_dir = base_dir / "data" / "raw" / "ViFinQA" / "financial_statements"
    csv_output_dir = base_dir / "data" / "processed" / "csv"
    
    if not raw_data_dir.exists():
        logger.error(f"Raw data directory does not exist: {raw_data_dir}")
        return
        
    csv_output_dir.mkdir(parents=True, exist_ok=True)
    
    parser = FinancialReportParser()
    
    # Collect all TXT files
    txt_files = list(raw_data_dir.rglob("*.txt"))
    logger.info(f"Found {len(txt_files)} TXT files to process.")
    
    success_count = 0
    error_count = 0
    
    for file_path in tqdm(txt_files, desc="Parsing TXT to CSV"):
        try:
            # Parse report
            report = (
                parser
                    .read(file_path)
                    .extract_metadata()
                    .split_pages()
                    .detect_tables()
                    .extract_tables()
                    .build()
            )
            
            # Extract metadata
            meta = report.metadata.additional_info
            # Fallback to path extraction if metadata is missing
            idx = file_path.parts.index("financial_statements")
            fallback_ticker = file_path.parts[idx + 1] if len(file_path.parts) > idx + 1 else "UNKNOWN"
            fallback_year = file_path.parts[idx + 2] if len(file_path.parts) > idx + 2 else "YYYY"
            
            ticker = meta.get("ticker", fallback_ticker)
            year = meta.get("year", fallback_year)
            
            # Export each table to CSV
            for page in report.pages:
                for i, table in enumerate(page.tables, 1):
                    # Table name matches the duckdb_table format we use later
                    table_name = f"{ticker}_{year}_page{page.page_number}_table{i}"
                    csv_path = csv_output_dir / f"{table_name}.csv"
                    
                    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        if table.headers:
                            writer.writerow(table.headers)
                        for row in table.rows:
                            # Pad row to match header length if needed
                            padded_row = row + [""] * (len(table.headers) - len(row))
                            writer.writerow(padded_row[:len(table.headers)])
                            
            success_count += 1
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            error_count += 1
            
    logger.info(f"Finished parsing. Success: {success_count}, Errors: {error_count}")
    logger.info(f"CSV files are saved in: {csv_output_dir}")

if __name__ == "__main__":
    main()
