import json
import zipfile
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent
CURRENT_SUBMISSION_ZIP = ROOT_DIR / "FINAL_PIPELINE_SUBMISSION.zip"
BASELINE_ZIP = ROOT_DIR / "prediction_result_2.zip"  # Hoặc prediction_result.zip

def load_json_from_zip(zip_path: Path) -> List[Dict[str, Any]]:
    if not zip_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as z:
        for filename in z.namelist():
            if filename.endswith("submission.json"):
                with z.open(filename) as f:
                    return json.load(f)
    raise ValueError(f"Không tìm thấy submission.json trong {zip_path}")

def format_num(val: Any) -> str:
    try:
        f = float(val)
        return f"{f:,.2f}"
    except Exception:
        return str(val)

def compare_submissions():
    print("=" * 90)
    print("🔍 BỘ CÔNG CỤ PHÂN TÍCH VÀ SO SÁNH GÓI NỘP BÀI (DIFF ANALYZER)")
    print("=" * 90)

    try:
        base_data = load_json_from_zip(BASELINE_ZIP)
        curr_data = load_json_from_zip(CURRENT_SUBMISSION_ZIP)
    except Exception as e:
        print(f"❌ Lỗi nạp dữ liệu: {e}")
        return

    base_map = {item["id"]: item for item in base_data}
    curr_map = {item["id"]: item for item in curr_data}

    total_q = len(curr_map)
    doc_match_cnt = 0
    table_match_cnt = 0
    ans_exact_cnt = 0
    ans_rel_cnt = 0
    diff_cases = []

    for q_id, curr_item in sorted(curr_map.items()):
        if q_id not in base_map:
            continue
        base_item = base_map[q_id]

        # 1. So sánh Documents
        base_docs = set(base_item.get("relevant_docs", []))
        curr_docs = set(curr_item.get("relevant_docs", []))
        is_doc_same = (base_docs == curr_docs)
        if is_doc_same:
            doc_match_cnt += 1

        # 2. So sánh Tables
        base_tbls = set(base_item.get("relevant_tables", []))
        curr_tbls = set(curr_item.get("relevant_tables", []))
        is_tbl_same = (base_tbls == curr_tbls)
        if is_tbl_same:
            table_match_cnt += 1

        # 3. So sánh Giá trị Đáp án
        base_ans = float(base_item.get("answer", 0.0))
        curr_ans = float(curr_item.get("answer", 0.0))
        
        is_exact = abs(base_ans - curr_ans) < 1e-4
        if is_exact:
            ans_exact_cnt += 1

        # Chấp nhận sai số tương đối 1%
        rel_diff = abs(base_ans - curr_ans) / (abs(base_ans) + 1e-9)
        is_rel_match = rel_diff <= 0.01
        if is_rel_match:
            ans_rel_cnt += 1

        if not is_exact or not is_tbl_same or not is_doc_same:
            diff_cases.append({
                "id": q_id,
                "question": curr_item.get("question", ""),
                "base_docs": list(base_docs),
                "curr_docs": list(curr_docs),
                "base_tbls": list(base_tbls),
                "curr_tbls": list(curr_tbls),
                "base_ans": base_ans,
                "curr_ans": curr_ans,
                "base_query": base_item.get("pandas_query", ""),
                "curr_query": curr_item.get("pandas_query", "")
            })

    print(f"📊 TỔNG QUAN ĐỐI SOÁT ({total_q} CÂU HỎI):")
    print(f"  • Khớp Document (Tài liệu) : {doc_match_cnt}/{total_q} ({doc_match_cnt/total_q*100:.1f}%)")
    print(f"  • Khớp Table (Bảng BCTC)   : {table_match_cnt}/{total_q} ({table_match_cnt/total_q*100:.1f}%)")
    print(f"  • Khớp Đáp án Tuyệt đối     : {ans_exact_cnt}/{total_q} ({ans_exact_cnt/total_q*100:.1f}%)")
    print(f"  • Khớp Đáp án Tương đối (1%): {ans_rel_cnt}/{total_q} ({ans_rel_cnt/total_q*100:.1f}%)")
    print("=" * 90)

    # Hiển thị 10 câu tiêu biểu có sự khác biệt
    print("🔎 CHI TIẾT 10 CÂU KHÁC BIỆT ĐIỂN HÌNH ĐỂ DEBUG:")
    for i, c in enumerate(diff_cases[:10], 1):
        print(f"\n[Case {i:02d}] Câu hỏi ID: {c['id']}")
        print(f"  ❓ Câu hỏi     : {c['question']}")
        print(f"  📄 Docs (Gốc)  : {c['base_docs']}  |  (Hiện tại): {c['curr_docs']}")
        print(f"  📑 Table (Gốc) : {c['base_tbls']}  |  (Hiện tại): {c['curr_tbls']}")
        print(f"  💡 Đáp án (Gốc): {format_num(c['base_ans'])}  |  (Hiện tại): {format_num(c['curr_ans'])}")
        print(f"  ⚙️ Query (Gốc) : {c['base_query']}")
        print(f"  ⚙️ Query (Mới) : {c['curr_query']}")

    # Lưu toàn bộ báo cáo phân tích ra file json
    report_file = ROOT_DIR / "comparison_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "metrics": {
                "total_questions": total_q,
                "doc_match_rate": doc_match_cnt / total_q,
                "table_match_rate": table_match_cnt / total_q,
                "ans_exact_match_rate": ans_exact_cnt / total_q,
                "ans_rel_match_rate": ans_rel_cnt / total_q
            },
            "diff_cases": diff_cases
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Toàn bộ danh sách {len(diff_cases)} câu lệch đã được lưu tại: comparison_report.json")
    print("=" * 90)

if __name__ == "__main__":
    compare_submissions()