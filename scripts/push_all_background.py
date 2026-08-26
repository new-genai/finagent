import sys
import logging
from pathlib import Path
from tqdm import tqdm
import multiprocessing
import traceback

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.parser.report_parser import FinancialReportParser
from src.metadata.builders import SchemaBuilder
from src.database.supabase_service import SupabaseService
from src.embedding.service import EmbeddingService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = ROOT / "data" / "raw" / "ViFinQA"

def process_file(fpath):
    parser = FinancialReportParser()
    schema_builder = SchemaBuilder()
    try:
        report = parser.parse(fpath)
        schemas = schema_builder.build_schema(report)
        return schemas
    except Exception as e:
        logger.error(f"Error parsing {fpath.name}: {e}")
        return []

def main():
    logger.info("Initializing Supabase and Embedding models...")
    db = SupabaseService()
    if not db.client:
        logger.error("Supabase client not initialized. Please check .env settings.")
        return
        
    embedder = EmbeddingService()
    
    txt_files = list(RAW_DIR.rglob("*.txt"))
    logger.info(f"Found {len(txt_files)} text files. Beginning parsing (Multi-processing)...")
    
    all_schemas = []
    
    # Process files in parallel to speed up the parsing phase
    with multiprocessing.Pool() as pool:
        for schemas in tqdm(pool.imap_unordered(process_file, txt_files), total=len(txt_files), desc="Parsing files"):
            if schemas:
                all_schemas.extend(schemas)
                
    logger.info(f"Parsing complete. Generated {len(all_schemas)} tables.")
    
    logger.info("Starting embedding generation and Supabase push...")
    chunk_size = 50
    for i in tqdm(range(0, len(all_schemas), chunk_size), desc="Pushing to Supabase"):
        chunk = all_schemas[i:i+chunk_size]
        records = []
        for doc in chunk:
            title = doc.get("title", "")
            headers = doc.get("headers", [])
            keywords = doc.get("keywords", [])
            
            vector = embedder.embed_table_schema(title, headers, keywords)
            
            headers_str = " | ".join(str(h) for h in headers) if headers else ""
            unique_rows = list(dict.fromkeys([str(k) for k in keywords]))[:20]
            row_str = " ; ".join(unique_rows)
            child_summary = (
                f"Tóm tắt Bảng tài chính:\n"
                f"- Ngữ cảnh: {title}\n"
                f"- Cột: {headers_str}\n"
                f"- Dòng: {row_str}\n"
            )

            records.append({
                "table_id": doc.get("table_id", ""),
                "duckdb_table": doc.get("duckdb_table", ""),
                "company": doc.get("company", ""),
                "year": str(doc.get("year", "")),
                "headers": [str(h) for h in headers],
                "keywords": [str(k) for k in keywords],
                "content": child_summary,
                "embedding": vector.tolist()
            })
            
        try:
            # We use upsert to avoid duplicate key errors if the user re-runs this script
            db.client.table("documents").upsert(records, on_conflict="table_id").execute()
        except Exception as e:
            logger.error(f"Error inserting chunk {i}-{i+len(chunk)}: {e}")

    logger.info("✅ Finished pushing ALL DATA to Supabase!")

if __name__ == "__main__":
    main()
