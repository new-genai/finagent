import sys
from pathlib import Path
import pickle

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import duckdb
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

GOLD_ID = "098639c9-9b85-4970-aa6f-55a420bc3f4e"
doc_store_path = ROOT_DIR / "data" / "index" / "doc_store.pkl"
db_path = ROOT_DIR / "data" / "finagent.db"

print("=" * 80)
print(f"1. KIỂM TRA ĐỊNH DẠNG DOC_STORE VÀ TÌM KIẾM KEY/ID: {GOLD_ID}")
print("=" * 80)

found_doc = None
if doc_store_path.exists():
    with open(doc_store_path, "rb") as f:
        store = pickle.load(f)
        print(f"Kiểu dữ liệu doc_store: {type(store).__name__} | Số lượng phần tử: {len(store)}")
        
        # Trường hợp 1: Dictionary
        if isinstance(store, dict):
            for k, v in store.items():
                if k == GOLD_ID or (isinstance(v, dict) and v.get("table_id") == GOLD_ID):
                    found_doc = v if isinstance(v, dict) else {k: v}
                    print(f"-> Khớp tại key: {k}")
                    break
        # Trường hợp 2: List
        elif isinstance(store, list):
            for item in store:
                if isinstance(item, dict) and item.get("table_id") == GOLD_ID:
                    found_doc = item
                    break

    if found_doc:
        print("🎯 Thông tin bảng vàng trích xuất được:")
        print(found_doc)
    else:
        print("❌ Không khớp ID trong doc_store.pkl. Lấy mẫu 3 phần tử đầu tiên để kiểm tra schema:")
        sample = list(store.items())[:3] if isinstance(store, dict) else store[:3]
        for s in sample:
            print(s)

print("\n" + "=" * 80)
print("2. QUÉT VÀ IN TẤT CẢ CÁC BẢNG CỦA VNM NĂM 2023 CÓ DỮ LIỆU TÀI CHÍNH:")
print("=" * 80)

conn = duckdb.connect(str(db_path), read_only=True)
tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall() if t[0].startswith("VNM_2023")]

for t_name in tables:
    df = conn.execute(f'SELECT * FROM "{t_name}"').df()
    # Lọc các bảng có từ 2 cột và nhiều hơn 2 dòng dữ liệu
    if df.shape[1] >= 2 and df.shape[0] >= 3:
        # Kiểm tra xem có cột tiền tệ / năm (2023)
        has_year_col = any("2023" in str(c) for c in df.columns)
        if has_year_col:
            print(f"\n🏷️ BẢNG: {t_name} | Kích thước: {df.shape}")
            print(f"Cột: {list(df.columns)}")
            print(df)
            print("-" * 80)

conn.close()