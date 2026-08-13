import os
import sys
import logging
import json
from pathlib import Path
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure python can find src
sys.path.append(str(Path(__file__).parent.parent))

from src.parser import FinancialReportParser
from src.metadata.builders import SchemaBuilder

def main():
    base_dir = Path(__file__).parent.parent
    raw_data_dir = base_dir / "data" / "raw" / "ViFinQA" / "financial_statements"
    metadata_dir = base_dir / "data" / "metadata"
    
    if not raw_data_dir.exists():
        logger.error(f"Raw data directory does not exist: {raw_data_dir}")
        return
        
    metadata_dir.mkdir(parents=True, exist_ok=True)
    schema_path = metadata_dir / "schemas.json"
    
    parser = FinancialReportParser()
    schema_builder = SchemaBuilder()
    
    # Collect all TXT files
    txt_files = list(raw_data_dir.rglob("*.txt"))
    logger.info(f"Found {len(txt_files)} TXT files to build metadata.")
    
    all_schemas = []
    success_count = 0
    error_count = 0
    
    for file_path in tqdm(txt_files, desc="Building Metadata"):
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
            
            # Since our parser doesn't perfectly extract ticker/year for all files
            # we inject it back into the report metadata using the path structure to be safe
            meta = report.metadata.additional_info
            idx = file_path.parts.index("financial_statements")
            fallback_ticker = file_path.parts[idx + 1] if len(file_path.parts) > idx + 1 else "UNKNOWN"
            fallback_year = file_path.parts[idx + 2] if len(file_path.parts) > idx + 2 else "YYYY"
            
            if "ticker" not in meta or meta["ticker"] == "UNKNOWN":
                meta["ticker"] = fallback_ticker
            if "year" not in meta or meta["year"] == "YYYY":
                meta["year"] = fallback_year
                
            # Build schema
            schemas = schema_builder.build_schema(report)
            all_schemas.extend(schemas)
            
            success_count += 1
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            error_count += 1
            
    # Save schemas to JSON
    with open(schema_path, 'w', encoding='utf-8') as f:
        json.dump(all_schemas, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Finished building schemas. Total schemas: {len(all_schemas)}")
    logger.info(f"Schemas saved to {schema_path}")

if __name__ == "__main__":
    main()
