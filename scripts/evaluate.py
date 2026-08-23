import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import time
import json
import re
import argparse
from datetime import datetime
from typing import List, Dict, Any
import requests

API_URL = "http://127.0.0.1:8000/api/chat"
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Dataset Benchmark đối chiếu chuẩn Leaderboard
BENCHMARK_GROUND_TRUTH = [
    {
        "id": 1,
        "question": "Doanh thu năm 2023 của FPT là bao nhiêu?",
        "gold_tables": ["bfcfcbe6-940b-4722-ae58-0558804af3cf", "6bec3b71-47b0-4961-a716-163d99a8c3c5"],
        "gold_numbers": [52625, 52625160, 52625.17, 953274],
        "unit_desc": "52.625 tỷ VND"
    },
    {
        "id": 2,
        "question": "Tính tổng doanh thu và lợi nhuận sau thuế của FPT năm 2023 là bao nhiêu?",
        "gold_tables": ["0d964c49-77d2-4657-8db6-5a1b3ab96705", "55aad705-c7d1-4cd7-9fa4-c0aa3eb7f3a6"],
        "gold_numbers": [52625, 7788, 953274, 510039, 60413],
        "unit_desc": "Doanh thu ~52.625 tỷ, LNST ~7.788 tỷ (hoặc tổng ~60.413 tỷ)"
    },
    {
        "id": 3,
        "question": "Số dư nợ xấu nhóm 5 của ACB cuối năm 2022 là bao nhiêu?",
        "gold_tables": ["22eca2dd-5a5b-4f48-b73c-14ec993b20ef"],
        "gold_numbers": [50000, 50, 2095],
        "unit_desc": "Số dư nợ xấu nhóm 5 của ACB"
    },
    {
        "id": 4,
        "question": "Lợi nhuận gộp năm 2023 của Vinamilk (VNM) là bao nhiêu?",
        "gold_tables": ["098639c9-9b85-4970-aa6f-55a420bc3f4e"],
        "gold_numbers": [22117681, 22117, 24500],
        "unit_desc": "Lợi nhuận gộp ~22.117 tỷ VND"
    },
    {
        "id": 5,
        "question": "Tổng tài sản của Tập đoàn Hòa Phát (HPG) năm 2023 là bao nhiêu tỷ đồng?",
        "gold_tables": ["9e134441-52d8-47c4-91c7-01825aa26500"],
        "gold_numbers": [187782, 187783, 96112, 1952],
        "unit_desc": "Tổng tài sản ~187.782 tỷ VND"
    }
]

def extract_numbers_from_text(text: str) -> List[float]:
    """Trích xuất tất cả số thực trong câu trả lời."""
    clean = re.sub(r'(\d+)\.(\d{3})', r'\1\2', text)
    clean = clean.replace(',', '.')
    matches = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", clean)
    res = []
    for m in matches:
        try:
            val = float(m)
            res.append(val)
        except Exception:
            pass
    return res

def compute_table_metrics(pred_tables: List[str], gold_tables: List[str]) -> Dict[str, float]:
    pred_set = set(pred_tables)
    gold_set = set(gold_tables)
    
    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    beta = 2.0
    if precision + recall > 0:
        f2 = (1 + beta**2) * (precision * recall) / ((beta**2 * precision) + recall)
    else:
        f2 = 0.0
        
    mrr = 0.0
    for idx, table_id in enumerate(pred_tables[:5], 1):
        if table_id in gold_set:
            mrr = 1.0 / idx
            break
            
    return {"precision": precision, "recall": recall, "f2": f2, "mrr5": mrr}

def run_evaluation(tests: List[Dict[str, Any]]):
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_txt = REPORTS_DIR / f"eval_report_{run_timestamp}.txt"
    report_md = REPORTS_DIR / f"eval_report_{run_timestamp}.md"
    report_json = REPORTS_DIR / f"eval_results_{run_timestamp}.json"
    
    terminal_logs = []
    md_sections = []
    
    def log_both(msg: str):
        print(msg)
        terminal_logs.append(msg)

    log_both("=" * 80)
    log_both(f"🚀 BẮT ĐẦU ĐÁNH GIÁ CHUẨN LEADERBOARD [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    log_both("=" * 80)

    md_sections.append(f"# 📊 BÁO CÁO ĐÁNH GIÁ CHI TIẾT FINAGENT ({run_timestamp})\n")
    md_sections.append(f"- **Thời gian chạy:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_sections.append(f"- **API Endpoint:** `{API_URL}`\n---")

    results = []
    exec_success_count = 0
    total_metrics = {"precision": 0.0, "recall": 0.0, "f2": 0.0, "mrr5": 0.0}

    for idx, item in enumerate(tests, 1):
        q = item["question"]
        gold_tables = item["gold_tables"]
        gold_numbers = item["gold_numbers"]
        unit_desc = item.get("unit_desc", "")
        
        log_both(f"\n{'━'*80}")
        log_both(f"📌 [CÂU {item['id']}/5]: {q}")
        log_both(f"{'━'*80}")
        log_both(f"🎯 Chuẩn BTC: Gold Tables={gold_tables} | Số mong đợi: {gold_numbers} ({unit_desc})")
        
        start_time = time.time()
        try:
            resp = requests.post(API_URL, json={"question": q}, timeout=180)
            elapsed = time.time() - start_time
            
            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "")
                thought = data.get("thought_process", "")
                tables_used = data.get("tables_used", [])
                
                metrics = compute_table_metrics(tables_used, gold_tables)
                for k in total_metrics:
                    total_metrics[k] += metrics[k]
                
                found_numbers = extract_numbers_from_text(answer)
                is_correct = any(
                    any(abs(fn - gn) < 1.0 or (gn != 0 and abs(fn - gn)/gn < 0.05) for gn in gold_numbers)
                    for fn in found_numbers
                )
                
                status_exec = "✅ ĐÚNG (PASS)" if is_correct else "❌ SAI / VETO"
                if is_correct:
                    exec_success_count += 1
                
                log_both(f"⏱️ Thời gian phản hồi: {elapsed:.2f}s | Trạng thái: {status_exec}")
                log_both(f"📊 Retrieval Score: F2={metrics['f2']:.4f} | Precision={metrics['precision']:.4f} | Recall={metrics['recall']:.4f} | MRR5={metrics['mrr5']:.4f}")
                log_both(f"📑 Bảng AI chọn: {tables_used}")
                log_both(f"🔍 Số AI trích xuất được: {found_numbers}")
                log_both(f"💬 Câu trả lời trả về:\n   {answer}")
                log_both(f"💻 Code & Trace Log:\n{thought}")

                # Ghi chi tiết vào file Markdown
                md_sections.append(f"\n## 📌 Câu {item['id']}: {q}")
                md_sections.append(f"- **Thời gian:** `{elapsed:.2f}s` | **Kết quả:** **{status_exec}**")
                md_sections.append(f"- **Đáp án chuẩn:** Bảng `{gold_tables}` | Số `{gold_numbers}` ({unit_desc})")
                md_sections.append(f"- **Bảng AI đã chọn:** `{tables_used}`")
                md_sections.append(f"- **Chỉ số Retrieval:** `F2={metrics['f2']:.4f}` | `P={metrics['precision']:.4f}` | `R={metrics['recall']:.4f}` | `MRR5={metrics['mrr5']:.4f}`")
                md_sections.append(f"\n### 💬 Câu trả lời của AI:\n> {answer}\n")
                md_sections.append(f"### 💻 Nhật ký phân tích & Code:\n```text\n{thought}\n```\n---")

                results.append({
                    "id": item["id"],
                    "question": q,
                    "elapsed_sec": round(elapsed, 2),
                    "status": status_exec,
                    "metrics": metrics,
                    "tables_used": tables_used,
                    "found_numbers": found_numbers,
                    "answer": answer,
                    "thought_process": thought
                })
            else:
                elapsed = time.time() - start_time
                err_msg = f"API Error (Status {resp.status_code}): {resp.text}"
                log_both(f"❌ {err_msg}")
                md_sections.append(f"\n## 📌 Câu {item['id']}: {q}\n- ⏱️ **Thời gian:** `{elapsed:.2f}s`\n- ❌ **Lỗi:** `{err_msg}`\n---")
                results.append({"id": item["id"], "question": q, "status": "ERROR", "error": err_msg})

        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            err_msg = f"Timeout sau {elapsed:.2f}s (Server xử lý quá 180s)"
            log_both(f"❌ LỖI KẾT NỐI: {err_msg}")
            md_sections.append(f"\n## 📌 Câu {item['id']}: {q}\n- ⏱️ **Thời gian:** `{elapsed:.2f}s`\n- ❌ **Lỗi:** `{err_msg}`\n---")
            results.append({"id": item["id"], "question": q, "status": "TIMEOUT", "error": err_msg})

        except Exception as e:
            elapsed = time.time() - start_time
            err_msg = str(e)
            log_both(f"❌ LỖI KẾT NỐI: {err_msg}")
            md_sections.append(f"\n## 📌 Câu {item['id']}: {q}\n- ⏱️ **Thời gian:** `{elapsed:.2f}s`\n- ❌ **Lỗi:** `{err_msg}`\n---")
            results.append({"id": item["id"], "question": q, "status": "ERROR", "error": err_msg})

    n = len(tests)
    final_exec_acc = exec_success_count / n if n > 0 else 0.0
    final_f2 = total_metrics["f2"] / n if n > 0 else 0.0
    final_p = total_metrics["precision"] / n if n > 0 else 0.0
    final_r = total_metrics["recall"] / n if n > 0 else 0.0
    final_mrr = total_metrics["mrr5"] / n if n > 0 else 0.0

    summary_banner = f"""
================================================================================
🏆 BẢNG KẾT QUẢ ĐỐI CHIẾU TRỰC TIẾP VỚI TOP 1 LEADERBOARD
================================================================================
Chỉ số                     | Điểm Của Bạn    | Top 1 (Vương)  
--------------------------------------------------------------------------------
EXECUTION ACCURACY         | {final_exec_acc:<15.4f} | 0.6700          
TABLES F2-MACRO            | {final_f2:<15.4f} | 0.4980          
TABLES PRECISION           | {final_p:<15.4f} | 0.6052          
TABLES RECALL              | {final_r:<15.4f} | 0.4927          
TABLES MRR5                | {final_mrr:<15.4f} | 0.6280          
================================================================================
"""
    log_both(summary_banner)

    summary_md = f"""
## 🏆 Bảng Điểm Tổng Hợp Đối Chiếu Leaderboard

| Chỉ số | Điểm Hệ Thống | Top 1 Leaderboard |
| :--- | :--- | :--- |
| **EXECUTION ACCURACY** | **`{final_exec_acc:.4f}`** | `0.6700` |
| **TABLES F2-MACRO** | **`{final_f2:.4f}`** | `0.4980` |
| **TABLES PRECISION** | **`{final_p:.4f}`** | `0.6052` |
| **TABLES RECALL** | **`{final_r:.4f}`** | `0.4927` |
| **TABLES MRR5** | **`{final_mrr:.4f}`** | `0.6280` |

---
"""
    md_sections.insert(2, summary_md)

    with open(report_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(terminal_logs))
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_sections))
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": run_timestamp,
            "summary": {
                "execution_accuracy": final_exec_acc,
                "f2_macro": final_f2,
                "precision": final_p,
                "recall": final_r,
                "mrr5": final_mrr
            },
            "details": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Toàn bộ hồ sơ kiểm tra đã được lưu tại:")
    print(f" 👉 Terminal Log : {report_txt}")
    print(f" 👉 Báo cáo MD   : {report_md}")
    print(f" 👉 Dữ liệu JSON : {report_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy đánh giá FinAgent Benchmark.")
    parser.add_argument(
        "--id", 
        type=int, 
        choices=[1, 2, 3, 4, 5], 
        help="Chỉ định ID câu hỏi muốn test riêng lẻ (1 đến 5). Bỏ trống để chạy toàn bộ."
    )
    args = parser.parse_args()

    selected_tests = BENCHMARK_GROUND_TRUTH
    if args.id:
        selected_tests = [item for item in BENCHMARK_GROUND_TRUTH if item["id"] == args.id]
        print(f"🎯 Đang chạy chế độ kiểm thử cô lập: Câu {args.id}...")

    run_evaluation(selected_tests)