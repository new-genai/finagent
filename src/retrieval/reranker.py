import logging
from typing import List
import torch
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Đang nạp mô hình Reranker: {model_name} trên thiết bị [{device.upper()}]...")
        self.model = CrossEncoder(model_name, max_length=256, device=device)

    def predict(self, pairs: List[List[str]]) -> List[float]:
        if not pairs:
            return []
        
        # CrossEncoder tự động tính ma trận chấm điểm trên GPU
        scores = self.model.predict(pairs, batch_size=32, show_progress_bar=False)
        if isinstance(scores, (list, tuple)):
            return list(scores)
        return scores.tolist()