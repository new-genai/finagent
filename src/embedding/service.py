import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Provides local text embedding using SentenceTransformers."""
    
    def __init__(self, model_name: str = "keepitreal/vietnamese-sbert"):
        """
        Khởi tạo model Embedding.
        Sử dụng SentenceTransformer chạy hoàn toàn offline (local).
        """
        logger.info(f"Loading embedding model: {model_name}")
        # Trì hoãn việc import SentenceTransformer để tránh bị chậm lúc khởi động app 
        # nếu không thực sự gọi tới tính năng này ngay lập tức.
        import torch
        try:
            torch.set_num_threads(8)
            torch.set_num_interop_threads(8)
        except Exception:
            pass
        from sentence_transformers import SentenceTransformer
        
        try:
            self.model = SentenceTransformer(model_name, device="cpu", local_files_only=True)
        except Exception:
            logger.warning("Embedding model is not cached locally; downloading from HuggingFace.")
            self.model = SentenceTransformer(model_name, device="cpu")
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")

    def embed_text(self, text: str) -> np.ndarray:
        """Sinh embedding cho một chuỗi text."""
        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Sinh embedding cho nhiều chuỗi text cùng lúc (tối ưu tốc độ)."""
        return self.model.encode(texts, convert_to_numpy=True)
        
    def embed_table_schema(self, title: str, headers: List[str], keywords: List[str]) -> np.ndarray:
        """
        Tạo embedding đại diện cho một bảng (Table).
        Gom nhóm title, headers và keywords thành một khối văn bản giàu ngữ nghĩa.
        """
        headers_str = ", ".join(str(h) for h in headers) if headers else "Không có cột"
        keywords_str = ", ".join(str(k) for k in keywords) if keywords else ""
        
        # Tạo chuỗi mô tả ngữ nghĩa
        combined_text = f"Bảng: {title}. Các cột: {headers_str}. Từ khóa: {keywords_str}"
        return self.embed_text(combined_text)
