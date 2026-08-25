import json
import zipfile
import shutil
from pathlib import Path
import requests

API_URL = "http://127.0.0.1:8000/api/chat"
ROOT_DIR = Path(__file__).resolve().parent

def build_submission():
    print("🚀 Bắt đầu đóng gói Submission...")
    
    # 1. Đọc bộ test từ file (Giả định bạn tạo file test_questions.json chứa câu hỏi)
    # Vì tôi chưa có file test của bạn, tôi tạo mock data để demo:
    test_data = [{"id": 1, "question": "Doanh thu năm 2022 của Vinamilk (VNM) là bao nhiêu?"}]
    
    out_dir = ROOT_DIR / "submission_temp"
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    submission_json = []
    
    for item in test_data:
        q_id = item["id"]
        q_text = item["question"]
        print(f"Đang xử lý câu {q_id}: {q_text}")
        
        res = requests.post(API_URL, json={"question": q_text}).json()
        
        # Bóc tách số float từ câu trả lời tự nhiên
        import re
        nums = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", res.get('answer', '0').replace(',', '.'))
        ans_float = float(nums[0]) if nums else 0.0
        
        sub_item = {
            "id": q_id,
            "question": q_text,
            "answer": ans_float,
            "relevant_docs": res.get("relevant_docs", []),
            "relevant_tables": res.get("relevant_tables", []),
            "evidence": res.get("evidence", []),
            "pandas_query": res.get("pandas_query", "")
        }
        submission_json.append(sub_item)
        
        # Copy các file CSV vào thư mục data/ của bài nộp
        for ev in res.get("evidence", []):
            csv_name = ev["csv_path"].split("/")[-1]
            src_csv = ROOT_DIR / "data" / "processed" / "csv" / csv_name
            if src_csv.exists():
                shutil.copy(src_csv, data_dir / csv_name)
                
    # Lưu file submission.json
    with open(out_dir / "submission.json", "w", encoding="utf-8") as f:
        json.dump(submission_json, f, ensure_ascii=False, indent=2)
        
    # Nén thành ZIP
    shutil.make_archive(ROOT_DIR / "submission", 'zip', out_dir)
    print("✅ Đã tạo xong file submission.zip! Bạn có thể nộp file này lên Leaderboard.")

if __name__ == "__main__":
    build_submission()
