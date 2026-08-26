import logging
from typing import List, Optional
import numpy as np

from src.schemas.core import RetrievedTable
from src.database.supabase_service import SupabaseService
from src.embedding.service import EmbeddingService

logger = logging.getLogger(__name__)

class DenseRetriever:
    def __init__(self, db_service: SupabaseService, embedding_service: EmbeddingService):
        self.db = db_service
        self.embedder = embedding_service

    def retrieve(
        self,
        query: str,
        company: Optional[str] = None,
        year: Optional[str] = None,
        top_k: int = 15
    ) -> List[RetrievedTable]:
        if not self.db.client or not self.embedder:
            return []

        try:
            # Sinh vector embedding cho câu hỏi bằng mô hình BGE-m3
            query_vector = self.embedder.embed_text(query).tolist()
            
            # Gọi RPC match_documents trên Supabase
            params = {
                "query_embedding": query_vector,
                "match_threshold": -1.0, # Ngưỡng similarity (BGE-m3 query vs long doc có thể âm)
                "match_count": top_k,
                "p_company": company.upper().strip() if company else None,
                "p_year": str(year).strip() if year else None
            }
            
            matched_docs = self.db.query_rpc("match_documents", params)
            
            results = []
            if matched_docs:
                for doc in matched_docs:
                    results.append(
                        RetrievedTable(
                            table_id=doc.get("table_id", "unknown"),
                            duckdb_table=doc.get("duckdb_table", "unknown"),
                            company=doc.get("company", "unknown"),
                            year=str(doc.get("year", "unknown")),
                            score=float(doc.get("similarity", 0.0)),
                            columns=doc.get("headers", [])
                        )
                    )
            return results
        except Exception as e:
            logger.error(f"Supabase dense retrieval error: {e}")
            return []