import faiss
import numpy as np
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class FAISSIndex:
    """Wrapper cho thư viện FAISS để tìm kiếm Vector (Dense Retrieval)."""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        # IndexFlatL2 sử dụng tính khoảng cách Euclidean (L2). 
        # Càng nhỏ càng giống nhau.
        self.index = faiss.IndexFlatL2(dimension)
        # Lưu trữ metadata. Key là chỉ số ID trong FAISS.
        self.doc_store: Dict[int, Dict[str, Any]] = {}
        
    def build(self, embeddings: np.ndarray, documents: List[Dict[str, Any]]) -> None:
        """Xây dựng index từ danh sách embeddings và documents (metadata)."""
        if len(embeddings) != len(documents):
            raise ValueError("Số lượng embeddings và documents phải bằng nhau.")
            
        self.index.add(embeddings)
        
        for i, doc in enumerate(documents):
            self.doc_store[i] = doc
            
        logger.info(f"Đã đưa {len(documents)} vectors vào FAISS.")

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Tìm kiếm top_k document gần nhất."""
        if self.index.ntotal == 0:
            return []
            
        # FAISS bắt buộc query phải là mảng 2D (batch)
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # FAISS trả về -1 nếu không tìm đủ số lượng trong CSDL nhỏ
            if idx != -1 and idx in self.doc_store:
                results.append((self.doc_store[idx], float(dist)))
                
        return results

    def save(self, filepath_prefix: Path) -> None:
        """Lưu trữ index và doc_store xuống đĩa cứng."""
        filepath_prefix.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(filepath_prefix.with_suffix('.faiss')))
        
        with open(filepath_prefix.with_suffix('.pkl'), 'wb') as f:
            pickle.dump(self.doc_store, f)
            
        logger.info(f"Đã lưu FAISS index tại {filepath_prefix}")

    def load(self, filepath_prefix: Path) -> None:
        """Nạp index từ đĩa cứng lên RAM."""
        faiss_path = str(filepath_prefix.with_suffix('.faiss'))
        pkl_path = filepath_prefix.with_suffix('.pkl')
        
        if Path(faiss_path).exists() and pkl_path.exists():
            self.index = faiss.read_index(faiss_path)
            with open(pkl_path, 'rb') as f:
                self.doc_store = pickle.load(f)
            logger.info(f"Đã nạp FAISS index với {self.index.ntotal} vectors.")
        else:
            logger.warning("Không tìm thấy file FAISS index.")
