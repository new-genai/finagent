import logging
import pickle
from pathlib import Path
from typing import List, Optional
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from src.schemas.core import RetrievedTable

logger = logging.getLogger(__name__)

class DenseRetriever:
    def __init__(
        self,
        index_path: str,
        doc_store_path: str,
        model_name: str = "BAAI/bge-small-en-v1.5"
    ):
        self.index = None
        self.doc_store = []
        self.embedder = None
        
        idx_p = Path(index_path)
        doc_p = Path(doc_store_path)

        if idx_p.exists() and doc_p.exists():
            logger.info("Đang nạp FAISS index...")
            self.index = faiss.read_index(str(idx_p))
            
            logger.info("Đang nạp doc_store...")
            with open(doc_p, "rb") as f:
                data = pickle.load(f)
                self.doc_store = data.get("doc_store", []) if isinstance(data, dict) else data
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Nạp mô hình Embedding: {model_name} trên thiết bị [{device.upper()}]...")
            self.embedder = SentenceTransformer(model_name, device=device)
        else:
            logger.warning("Không tìm thấy faiss.index hoặc doc_store.pkl. Hãy kiểm tra đường dẫn!")

    def retrieve(
        self,
        query: str,
        company: Optional[str] = None,
        year: Optional[str] = None,
        top_k: int = 15
    ) -> List[RetrievedTable]:
        if not self.index or not self.embedder or len(self.doc_store) == 0:
            return []

        with torch.no_grad():
            query_vector = self.embedder.encode([query], normalize_embeddings=True)
            query_vector = np.array(query_vector).astype("float32")

        # Quét sâu 1500 vectors để đảm bảo không lọc mất bảng mục tiêu
        search_k = min(1500, len(self.doc_store))
        distances, indices = self.index.search(query_vector, search_k)

        norm_company = company.upper().strip() if company else ""
        norm_year = str(year).strip() if year else ""

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.doc_store):
                continue
            
            doc = self.doc_store[idx]
            doc_comp = str(doc.get("company", "")).upper().strip()
            doc_yr = str(doc.get("year", "")).strip()

            if norm_company and doc_comp and doc_comp != norm_company:
                continue
            if norm_year and doc_yr and doc_yr != norm_year:
                continue

            results.append(
                RetrievedTable(
                    table_id=doc.get("table_id", "unknown"),
                    duckdb_table=doc.get("duckdb_table", ""),
                    company=doc.get("company", "unknown"),
                    year=str(doc.get("year", "unknown")),
                    score=float(dist),
                    columns=[str(h) for h in doc.get("headers", [])]
                )
            )

            if len(results) >= top_k:
                break

        return results