import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

class BM25Retriever:
    """Tìm kiếm từ khóa thô (Sparse Retrieval) bằng thuật toán BM25."""
    
    def __init__(self):
        self.bm25 = None
        self.doc_store: List[Dict[str, Any]] = []
        
    def _tokenize(self, text: str) -> List[str]:
        """Tách từ cơ bản."""
        return text.lower().split()

    def build(self, documents: List[Dict[str, Any]]) -> None:
        """Xây dựng thuật toán thống kê BM25 dựa trên corpus văn bản."""
        self.doc_store = documents
        
        corpus = []
        for doc in documents:
            title = doc.get("title", "")
            headers = " ".join([str(h) for h in doc.get("headers", [])])
            keywords = " ".join([str(k) for k in doc.get("keywords", [])])
            
            # Gộp mọi chữ cái thành 1 đoạn văn để phân tích tần suất
            combined = f"{title} {headers} {keywords}"
            corpus.append(self._tokenize(combined))
            
        self.bm25 = BM25Okapi(corpus, b=0.0)
        logger.info(f"Đã xây dựng BM25 index cho {len(documents)} documents.")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Tìm kiếm tài liệu sát với từ khóa nhất."""
        if not self.bm25:
            return []
            
        tokenized_query = self._tokenize(query)
        # Tính điểm BM25 cho tất cả văn bản trong hệ thống
        scores = self.bm25.get_scores(tokenized_query)
        
        # Sắp xếp (Sort) lấy các điểm cao nhất
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_n:
            if scores[idx] > 0: # Lọc bỏ rác không match từ nào
                results.append((self.doc_store[idx], float(scores[idx])))
                
        return results

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({"bm25": self.bm25, "doc_store": self.doc_store}, f)
        logger.info(f"Đã lưu BM25 index tại {filepath}")

    def load(self, filepath: Path) -> None:
        if filepath.exists():
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.bm25 = data["bm25"]
                self.doc_store = data["doc_store"]
            logger.info("Đã nạp BM25 index.")
        else:
            logger.warning("Không tìm thấy file BM25 index.")
