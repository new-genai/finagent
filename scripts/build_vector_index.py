import os
import sys
import pickle
import logging
from pathlib import Path
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# Thêm thư mục gốc vào path để import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def build_index():
    index_path = settings.INDEX_DIR / "faiss.index"
    bm25_path = settings.INDEX_DIR / "bm25.pkl"

    if not bm25_path.exists():
        logger.error(f"Không tìm thấy file: {bm25_path}")
        return

    logger.info("Đang đọc metadata từ bm25.pkl...")
    with open(bm25_path, "rb") as f:
        data = pickle.load(f)
    doc_store = data.get("doc_store", []) if isinstance(data, dict) else data

    # Sử dụng mô hình BAAI/bge-small-en-v1.5 siêu nhẹ (~130MB, tiêu tốn < 400MB RAM)
    model_name = "BAAI/bge-small-en-v1.5"
    logger.info(f"Đang nạp mô hình Embedding: {model_name} (chạy CPU an toàn)...")
    model = SentenceTransformer(model_name, device="cpu")
    model.max_seq_length = 256

    logger.info(f"Chuẩn bị dữ liệu cho {len(doc_store)} bảng...")
    texts = []
    for doc in doc_store:
        headers = " ".join([str(h) for h in doc.get("headers", [])])
        keywords = " ".join([str(k) for k in doc.get("keywords", [])[:15]])
        # Cắt ngắn văn bản để tránh phình bộ nhớ
        combined = f"{headers} {keywords}".strip()[:300]
        texts.append(combined if combined else "empty table")

    logger.info("Bắt đầu nhúng Vector (Batch Size = 64)...")
    with torch.no_grad():
        embeddings = model.encode(
            texts,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True
        )

    embeddings = np.array(embeddings).astype("float32")

    logger.info("Đang xây dựng và lưu không gian FAISS Index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Cosine Similarity cho vector đã chuẩn hóa
    index.add(embeddings)

    faiss.write_index(index, str(index_path))
    logger.info(f"✅ HOÀN TẤT! Đã tạo thành công file Vector tại: {index_path}")

if __name__ == "__main__":
    build_index()