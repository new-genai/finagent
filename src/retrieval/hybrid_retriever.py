import logging
from typing import List, Dict, Any

from .vector_index import FAISSIndex
from .bm25_retriever import BM25Retriever
from src.embedding.service import EmbeddingService
from src.schemas.core import RetrievedTable

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Hệ thống kết hợp FAISS (Dense/Ngữ nghĩa) và BM25 (Sparse/Từ khóa) 
    sử dụng thuật toán Reciprocal Rank Fusion (RRF).
    """
    
    def __init__(self, faiss_index: FAISSIndex, bm25_retriever: BM25Retriever, embedder: EmbeddingService):
        self.faiss = faiss_index
        self.bm25 = bm25_retriever
        self.embedder = embedder
        
    def _rrf(self, list_ranks: List[List[str]], k: int = 60) -> Dict[str, float]:
        """
        Reciprocal Rank Fusion.
        Công thức: Điểm = 1 / (k + Hạng)
        Giúp trộn kết quả của 2 hệ thống tìm kiếm hoàn toàn khác nhau một cách công bằng.
        """
        rrf_scores = {}
        for ranks in list_ranks:
            for rank, doc_id in enumerate(ranks):
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0.0
                rrf_scores[doc_id] += 1.0 / (k + rank + 1)
        return rrf_scores

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedTable]:
        """Thực thi Hybrid Search và trả về Top K documents tốt nhất."""
        logger.info(f"Hybrid retrieval for query: '{query}'")
        
        # 1. Tìm theo Sparse (Từ khoá) - BM25
        # Lấy gấp đôi số lượng cần thiết để có đủ mẫu mix
        bm25_results = self.bm25.search(query, top_k=top_k*2)
        
        # 2. Tìm theo Dense (Ngữ nghĩa) - FAISS
        query_emb = self.embedder.embed_text(query)
        faiss_results = self.faiss.search(query_emb, top_k=top_k*2)
        
        # Trích xuất danh sách table_id
        bm25_ranks = [doc["table_id"] for doc, score in bm25_results]
        faiss_ranks = [doc["table_id"] for doc, score in faiss_results]
        
        # 3. Kết hợp và tính điểm RRF
        rrf_scores = self._rrf([bm25_ranks, faiss_ranks])
        
        # Sắp xếp lại dựa trên RRF score tổng
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        final_top_ids = sorted_ids[:top_k]
        
        # Map ID ngược lại thành Document Object gốc để trả về cho User
        doc_lookup = {}
        for doc, _ in bm25_results + faiss_results:
            doc_lookup[doc["table_id"]] = doc
            
        final_results = []
        for doc_id in final_top_ids:
            doc = doc_lookup[doc_id]
            logger.info(f"DEBUG RETRIEVED DOC: {doc}")
            final_results.append(
                RetrievedTable(
                    table_id=doc.get("table_id", "unknown"),
                    duckdb_table=doc.get("duckdb_table", ""),
                    company=doc.get("company", "unknown"),
                    year=doc.get("year", "unknown"),
                    score=rrf_scores[doc_id],
                    columns=[str(h) for h in doc.get("headers", [])]
                )
            )
            
        return final_results
