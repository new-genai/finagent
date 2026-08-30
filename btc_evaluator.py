import json
import zipfile
import pandas as pd
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
ZIP_PATH = ROOT_DIR / "FINAL_PIPELINE_SUBMISSION.zip"

print("=" * 85)
print("⚖️ BỘ ĐÁNH GIÁ CHUẨN HOÁ THEO QUY TẮC SANDBOX CỦA BAN TỔ CHỨC...")
print("=" * 85)

if not ZIP_PATH.exists():
    print("❌ Lỗi: Không tìm thấy file FINAL_PIPELINE_SUBMISSION.zip")
    exit(1)

with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    file_list = set(z.namelist())
    
    if "submission.json" not in file_list:
        print("❌ Lỗi: Thiếu submission.json trong tệp zip!")
        exit(1)
        
    with z.open("submission.json") as f:
        submission = json.load(f)

    total_questions = len(submission)
    valid_format = 0
    valid_csv_exists = 0
    exec_success = 0
    non_zero_answers = 0
    hardcoded_queries = 0

    for item in submission:
        q_id = item.get("id")
        q_text = item.get("question", "")
        p_query = item.get("pandas_query", "")
        evidence = item.get("evidence", [])
        ans = item.get("answer", 0.0)

        # 1. Định dạng JSON
        if all(k in item for k in ["id", "question", "answer", "relevant_docs", "relevant_tables", "evidence", "pandas_query"]):
            valid_format += 1

        # 2. File CSV tồn tại
        if evidence and evidence[0].get("csv_path") in file_list:
            valid_csv_exists += 1
            csv_path = evidence[0]["csv_path"]

            # 3. Chạy Sandbox thực thi
            try:
                with z.open(csv_path) as cf:
                    df1 = pd.read_csv(cf)
                
                # Kiểm tra hardcode số lớn không dùng df1
                if "df1" not in p_query and re.search(r'\d{5,}', p_query):
                    hardcoded_queries += 1

                res = float(eval(p_query, {"__builtins__": None}, {"df1": df1, "float": float, "abs": abs}))
                
                if not pd.isna(res) and abs(res) != float('inf'):
                    exec_success += 1
                    if abs(res) > 1e-5:
                        non_zero_answers += 1
            except Exception:
                pass

    print(f"📊 BÁO CÁO ĐÁNH GIÁ THỰC TẾ TRÊN {total_questions} CÂU:")
    print(f"   • Hợp lệ cấu trúc submission.json       : {valid_format:>4d}/{total_questions} ({valid_format/total_questions*100:.1f}%)")
    print(f"   • File CSV bằng chứng trỏ đúng         : {valid_csv_exists:>4d}/{total_questions} ({valid_csv_exists/total_questions*100:.1f}%)")
    print(f"   • Thực thi Pandas Query thành công 100%: {exec_success:>4d}/{total_questions} ({exec_success/total_questions*100:.1f}%)")
    print(f"   • Số câu có giá trị thực tế (Khác 0.00): {non_zero_answers:>4d}/{total_questions} ({non_zero_answers/total_questions*100:.1f}%)")
    print(f"   • Số câu bị lỗi hardcode số tĩnh        : {hardcoded_queries:>4d}")
    print("=" * 85)