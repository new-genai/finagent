import pickle
import logging
from pathlib import Path
import duckdb
import pandas as pd
import sys
import os

# Thêm đường dẫn thư mục gốc để import được src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enrich_bm25_index():
    index_path = settings.INDEX_DIR / "bm25.pkl"
    db_path = settings.DB_PATH

    if not index_path.exists():
        logger.error(f"Không tìm thấy file index tại {index_path}")
        return

    # 1. Đọc file bm25.pkl hiện tại
    logger.info("Đang nạp file BM25 Index gốc...")
    with open(index_path, "rb") as f:
        data = pickle.load(f)
    
    # Xử lý cấu trúc lưu trữ (có thể là list hoặc dict)
    doc_store = data.get("doc_store", []) if isinstance(data, dict) else data

    # 2. Kết nối tới DuckDB
    logger.info(f"Kết nối tới cơ sở dữ liệu DuckDB: {db_path}")
    conn = duckdb.connect(str(db_path), read_only=True)

    # 3. Quét và nhồi dữ liệu Cột 1 vào keywords
    enriched_count = 0
    for doc in doc_store:
        table_name = doc.get("duckdb_table") or doc.get("table_id")
        if not table_name:
            continue
            
        try:
            # Truy xuất bảng từ DuckDB (lấy tối đa 100 dòng là đủ cho báo cáo tài chính)
            df = conn.execute(f'SELECT * FROM "{table_name}" LIMIT 100').df()
            if df.empty:
                continue
                
            first_col = df.columns[0]
            
            # Lấy các giá trị chữ độc nhất trong cột đầu tiên (loại bỏ NaN)
            row_labels = df[first_col].dropna().astype(str).unique().tolist()
            
            # Khởi tạo tập hợp keywords cũ để không bị trùng lặp
            existing_keywords = set(doc.get("keywords", []))
            
            for label in row_labels:
                # Chỉ lấy những chuỗi có ý nghĩa (bỏ qua khoảng trắng hoặc số dư thừa)
                clean_label = label.strip()
                if len(clean_label) > 1:
                    existing_keywords.add(clean_label)
            
            # Cập nhật lại keywords cho bảng này
            doc["keywords"] = list(existing_keywords)
            enriched_count += 1
            
        except Exception as e:
            # Bỏ qua ngầm nếu có bảng bị lỗi định dạng
            pass

    # 4. Lưu lại đè lên file bm25.pkl
    logger.info(f"Đang ghi đè {enriched_count} bảng đã được làm giàu dữ liệu...")
    new_data = {"bm25": data.get("bm25") if isinstance(data, dict) else None, "doc_store": doc_store}
    with open(index_path, "wb") as f:
        pickle.dump(new_data, f)
        
    conn.close()
    logger.info("✅ HOÀN TẤT! Dữ liệu dòng đã được nhúng thành công vào Index.")

if __name__ == "__main__":
    enrich_bm25_index()