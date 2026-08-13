import os
import sys
import logging
import json
import shutil
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure python can find src
sys.path.append(str(Path(__file__).parent.parent))

from src.loader.duckdb_manager import DuckDBManager
from src.embedding.service import EmbeddingService
from src.retrieval import FAISSIndex, BM25Retriever
from src.core.config import settings

def main():
    base_dir = Path(__file__).parent.parent
    csv_dir = base_dir / "data" / "processed" / "csv"
    metadata_dir = base_dir / "data" / "metadata"
    index_dir = base_dir / "data" / "index"
    
    schema_path = metadata_dir / "schemas.json"
    
    if not csv_dir.exists() or not schema_path.exists():
        logger.error("Please run preprocess_data.py and build_metadata.py first!")
        return
        
    index_dir.mkdir(parents=True, exist_ok=True)
    
    allowed_tickers = {'VNM', 'HPG', 'FPT', 'MWG', 'VJC', 'ACB', 'FTS', 'SCR', 'VSC', 'HT1', 'SAM', 'SSH'}
    allowed_years = {'2022', '2023'}
    
    # 1. Load CSVs to DuckDB
    logger.info("--- Step 1: Loading CSVs into DuckDB ---")
    # If the DB already exists, we will delete it to do a fresh run
    db_path = base_dir / "data" / "finagent.db"
    if db_path.exists():
        logger.info(f"Removing old finagent.db at {db_path}")
        try:
            # Need to make sure no process is holding a lock on the DB
            os.remove(db_path)
            # Remove wal if exists
            if Path(str(db_path) + ".wal").exists():
                os.remove(str(db_path) + ".wal")
        except Exception as e:
            logger.warning(f"Could not remove old db: {e}")
            
    db_manager = DuckDBManager(db_path=str(db_path))
    db_manager.load(csv_dir, allowed_tickers=allowed_tickers, allowed_years=allowed_years)
    db_manager.close()
    
    # 2. Build FAISS and BM25 Indexes
    logger.info("--- Step 2: Building Vector & Keyword Indexes ---")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schemas = json.load(f)
        
    if allowed_tickers or allowed_years:
        schemas = [
            s for s in schemas 
            if (not allowed_tickers or str(s.get("company", "")).upper() in allowed_tickers)
            and (not allowed_years or str(s.get("year", "")) in allowed_years)
        ]
        
    embedder = EmbeddingService()
    faiss_idx = FAISSIndex(dimension=embedder.dimension)
    bm25_idx = BM25Retriever()
    
    import re
    def clean_text(t):
        t = re.sub(r'<[^>]+>', ' ', t)
        t = re.sub(r'\s+', ' ', t)
        return t.strip()[:500]

    # Create combined text for embedding
    texts = []
    for s in schemas:
        header_str = " ".join([str(h) for h in s.get("headers", [])])
        keywords_str = " ".join([str(k) for k in s.get("keywords", [])])
        # The text format: Title + Headers + Keywords
        text = f"{s.get('title', '')} {header_str} {keywords_str}"
        text = clean_text(text)
        texts.append(text)
        
    logger.info(f"Embedding {len(texts)} documents...")
    embeddings = embedder.embed_batch(texts)
    
    logger.info("Building FAISS index...")
    faiss_idx.build(embeddings, schemas)
    faiss_idx.save(index_dir / "faiss")
    
    logger.info("Building BM25 index...")
    bm25_idx.build(schemas)
    bm25_idx.save(index_dir / "bm25.pkl")
    
    logger.info(f"Successfully built all indexes in {index_dir}")
    logger.info(f"DuckDB database saved at {db_path}")

if __name__ == "__main__":
    main()
