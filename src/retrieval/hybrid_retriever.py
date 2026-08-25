import logging
from typing import List, Optional
from src.schemas.core import RetrievedTable

logger = logging.getLogger(__name__)

class HybridRetriever:
    def __init__(self, bm25_retriever, dense_retriever, reranker=None):
        self.bm25_retriever = bm25_retriever
        self.dense_retriever = dense_retriever

    def retrieve(self, query: str, company: Optional[str] = None, year: Optional[str] = None, top_k: int = 3) -> List[RetrievedTable]:
        # Tìm kiếm độc lập trên 2 thuật toán
        bm25_results = self.bm25_retriever.retrieve(query, company, year, top_k=top_k * 2)
        dense_results = self.dense_retriever.retrieve(query, company, year, top_k=top_k * 2)
        
        # Thuật toán RRF (Reciprocal Rank Fusion)
        rrf_scores = {}
        tables_dict = {}
        
        for rank, doc in enumerate(bm25_results):
            rrf_scores[doc.table_id] = rrf_scores.get(doc.table_id, 0.0) + 1.0 / (60 + rank)
            tables_dict[doc.table_id] = doc
            
        for rank, doc in enumerate(dense_results):
            rrf_scores[doc.table_id] = rrf_scores.get(doc.table_id, 0.0) + 1.0 / (60 + rank)
            tables_dict[doc.table_id] = doc
            
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            doc = tables_dict[doc_id]
            doc.score = score
            results.append(doc)
            
        return results

    def retrieve_single(self, sub_query: str, company: Optional[str] = None, year: Optional[str] = None, top_k: int = 3) -> List[RetrievedTable]:
        return self.retrieve(sub_query, company, year, top_k)