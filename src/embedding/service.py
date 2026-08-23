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
        PARENT-CHILD RETRIEVAL:
        Tạo đoạn Tóm tắt ngữ nghĩa (Summary Chunk - Child Node) đại diện cho Parent Table.
        """
        headers_str = " | ".join(str(h) for h in headers) if headers else "Không có tiêu đề cột"
        
        # Rút gọn dòng (chỉ lấy 20 chỉ tiêu đầu tiên để đại diện cho toàn bộ bảng)
        unique_rows = list(dict.fromkeys([str(k) for k in keywords]))[:20]
        row_str = " ; ".join(unique_rows)
        
        # Child Node Summary (Đoạn tóm tắt được Vector hóa)
        child_summary = (
            f"Tóm tắt Bảng tài chính (Child Node):\n"
            f"- Ngữ cảnh: {title}\n"
            f"- Cấu trúc không gian - Cột (Columns): {headers_str}\n"
            f"- Cấu trúc không gian - Dòng (Rows): {row_str}\n"
            f"-> Bảng này (Parent Table) chứa số liệu chi tiết của các chỉ tiêu trên. "
            f"Dùng bảng này để tra cứu và trả lời câu hỏi về {headers_str}."
        )
        
        # Embed cái Summary Chunk này thay vì chuỗi phẳng. 
        # Khi Retriever tìm thấy nó, ID của Parent Table sẽ được trả về để bốc nguyên DataFrame.
        return self.embed_text(child_summary)
