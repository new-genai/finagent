from pathlib import Path
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "data" / "processed" / "csv"
DB_PATH = ROOT / "data" / "finagent.db"

GOLD_IDS = [
    "bfcfcbe6-940b-4722-ae58-0558804af3cf",
    "6bec3b71-47b0-4961-a716-163d99a8c3c5"
]

print("=" * 80)
print("TRA CỨU TRỰC TIẾP DỮ LIỆU BẢNG VÀNG TỪ DUCKDB & CSV")
print("=" * 80)

# 1. Tìm trong thư mục CSV
found_csv = False
if CSV_DIR.exists():
    for csv_path in CSV_DIR.glob("*.csv"):
        for gid in GOLD_IDS:
            if gid in csv_path.name:
                found_csv = True
                print(f"\n🎯 [CSV] Tìm thấy file: {csv_path.name}")
                df = pd.read_csv(csv_path)
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print("Dữ liệu mẫu:")
                print(df.head(10).to_string())

# 2. Tìm trong DuckDB
if DB_PATH.exists():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    tables = con.execute("SHOW TABLES").fetchall()
    print(f"\nTổng số bảng trong DuckDB: {len(tables)}")
    
    # Lọc các bảng của FPT năm 2023
    fpt_tables = [t[0] for t in tables if "FPT" in t[0].upper() and "2023" in t[0]]
    print(f"Các bảng FPT 2023 tìm thấy ({len(fpt_tables)} bảng): {fpt_tables[:10]}")
    
    for t_name in fpt_tables:
        df_sample = con.execute(f'SELECT * FROM "{t_name}"').df()
        # Tìm xem có bảng nào chứa số liệu doanh thu ~52.625 tỷ không
        text_dump = df_sample.to_string()
        if "52" in text_dump or "doanh thu" in text_dump.lower():
            print(f"\n⭐ [DuckDB Khả nghi] Bảng: {t_name}")
            print(f"Columns: {list(df_sample.columns)}")
            print(df_sample.head(8).to_string())