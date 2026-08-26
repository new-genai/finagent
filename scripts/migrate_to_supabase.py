import sys
import pickle
import logging
from pathlib import Path
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.database.supabase_service import SupabaseService
from src.embedding.service import EmbeddingService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INDEX_DIR = ROOT / "data" / "index"

def main():
    logger.info("Initializing Supabase and Embedding models...")
    db = SupabaseService()
    if not db.client:
        logger.error("Supabase client not initialized. Please check .env settings.")
        return
        
    embedder = EmbeddingService()
    
    bm25_file = INDEX_DIR / "bm25.pkl"
    if not bm25_file.exists():
        logger.error(f"Cannot find {bm25_file}. Run build_index.py first.")
        return
        
    with open(bm25_file, "rb") as f:
        data = pickle.load(f)
        doc_store = data.get("doc_store", []) if isinstance(data, dict) else data

    if not doc_store:
        logger.warning("doc_store is empty.")
        return

    logger.info(f"Found {len(doc_store)} tables to migrate to Supabase.")
    
    # Process and upload in chunks
    chunk_size = 50
    for i in tqdm(range(0, len(doc_store), chunk_size)):
        chunk = doc_store[i:i+chunk_size]
        records = []
        for doc in chunk:
            # Generate Embedding using parent-child approach
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
            
        # Push to Supabase
        try:
            db.client.table("documents").insert(records).execute()
        except Exception as e:
            logger.error(f"Error inserting chunk {i}-{i+len(chunk)}: {e}")

    logger.info("✅ Migration to Supabase completed!")

if __name__ == "__main__":
    main()
