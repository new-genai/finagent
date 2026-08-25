import sys
from pathlib import Path
import re
import pickle

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_CSV_DIR = ROOT_DIR / "data" / "processed" / "csv"
INDEX_DIR = ROOT_DIR / "data" / "index"

GOLD_ID = "098639c9-9b85-4970-aa6f-55a420bc3f4e"
TARGET_NUMS = ["22117", "22.117", "22,117", "22117681"]

print("=" * 80)
print("1. QUÉT TỆP NGUỒN (data/raw/) CỦA VNM NĂM 2023:")
print("=" * 80)

raw_vnm_files = list(RAW_DIR.rglob("*VNM*2023*")) + list(RAW_DIR.rglob("*vnm*2023*"))
print(f"-> Tìm thấy {len(raw_vnm_files)} file raw liên quan đến VNM 2023:")

for rf in raw_vnm_files:
    print(f"   + {rf.relative_to(ROOT_DIR)}")
    try:
        content = rf.read_text(encoding="utf-8", errors="ignore")
        found_targets = [num for num in TARGET_NUMS if num in content]
        if found_targets:
            print(f"     🎯 TÌM THẤY SỐ MỤC TIÊU {found_targets} TRONG FILE NÀY!")
            # In thử 3 dòng ngữ cảnh quanh số đó
            for line in content.splitlines():
                if any(num in line for num in found_targets):
                    print(f"        [Dòng]: {line.strip()[:150]}")
        else:
            print("     ❌ Không chứa số 22.117")
    except Exception as e:
        print(f"     Lỗi đọc file: {e}")

print("\n" + "=" * 80)
print(f"2. TRUY TÌM TABLE ID VÀNG ({GOLD_ID}) TRONG TẤT CẢ FILE INDEX/METADATA:")
print("=" * 80)

# Quét tất cả file pickle trong data/index
for pkl_file in INDEX_DIR.glob("*.pkl"):
    try:
        with open(pkl_file, "rb") as f:
            data = pickle.load(f)
            doc_list = []
            if isinstance(data, dict):
                if "doc_store" in data:
                    doc_list = data["doc_store"]
                else:
                    doc_list = list(data.values())
            elif isinstance(data, list):
                doc_list = data

            found = [d for d in doc_list if isinstance(d, dict) and d.get("table_id") == GOLD_ID]
            if found:
                print(f"🎯 TÌM THẤY {GOLD_ID} TRONG FILE: {pkl_file.name}")
                print(found[0])
            else:
                print(f"❌ Không có trong {pkl_file.name} (tổng số doc: {len(doc_list)})")
    except Exception as e:
        print(f"Lỗi đọc {pkl_file.name}: {e}")

print("\n" + "=" * 80)
print("3. QUÉT TẤT CẢ CSV ĐÃ EXTRACT (data/processed/csv/) TÌM SỐ 22.117:")
print("=" * 80)

matched_csv = []
if PROCESSED_CSV_DIR.exists():
    for cf in PROCESSED_CSV_DIR.glob("*.csv"):
        try:
            txt = cf.read_text(encoding="utf-8", errors="ignore")
            if any(num in txt for num in TARGET_NUMS):
                matched_csv.append(cf.name)
        except Exception:
            continue

if matched_csv:
    print(f"🎯 Tìm thấy số 22.117 trong các file CSV sau ({len(matched_csv)} files):")
    for name in matched_csv[:10]:
        print(f"   + {name}")
else:
    print("❌ Không có bất kỳ file CSV nào trong data/processed/csv/ chứa số 22.117!")