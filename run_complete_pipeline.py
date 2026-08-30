import json
import re
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from bs4 import BeautifulSoup
import pandas as pd
from rank_bm25 import BM25Okapi
import numpy as np
from groq import Groq

from src.metadata.normalizer import FinancialDataCleaner
from src.orchestration.smart_router import FULL_COMPANY_MAP, STOP_WORDS

ROOT_DIR = Path(__file__).resolve().parent
TEST_FILE_PATH = ROOT_DIR / "data" / "raw" / "ViFinQA" / "questions" / "questions.jsonl"
RAW_DIR = ROOT_DIR / "data" / "raw"
OUT_DIR = ROOT_DIR / "complete_submission_package"
DATA_DIR = OUT_DIR / "data"

GROQ_CLIENT = Groq(
    api_key=""
)

try:
    ACTIVE_MODELS = [m.id for m in GROQ_CLIENT.models.list().data if "whisper" not in m.id]
except Exception:
    ACTIVE_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

FULL_COMPANY_MAP.update({
    "pc1": "PC1", "tập đoàn pc1": "PC1", "xây lắp điện 1": "PC1",
    "sam": "SAM", "sam holdings": "SAM",
    "dxs": "DXS", "đất xanh services": "DXS",
    "cii": "CII", "bamboo capital": "BCG", "bluemarq group": "BCG", "bluemarq": "BCG",
    "vận tải dầu khí": "PVT", "lọc hóa dầu": "BSR", "xăng dầu việt nam": "PLX",
    "ngoại thương": "VCB", "vietcombank": "VCB", "vietjet": "VJC", "eximbank": "EIB",
    "hòa phát": "HPG", "hoa sen": "HSG", "nam kim": "NKG", "thế giới di động": "MWG",
    "masan": "MSN", "sunshine homes": "SSH", "vinhomes": "VHM", "vingroup": "VIC"
})

FINANCIAL_METRICS = [
    "lợi nhuận sau thuế chưa phân phối", "lợi nhuận sau thuế thu nhập doanh nghiệp", "lợi nhuận sau thuế", 
    "lợi nhuận kế toán sau thuế", "lợi nhuận trước thuế", "lợi nhuận kế toán trước thuế",
    "lợi nhuận gộp", "lợi nhuận thuần từ hoạt động kinh doanh", "lợi nhuận thuần",
    "doanh thu thuần", "doanh thu bán hàng và cung cấp dịch vụ", "doanh thu bán hàng", "doanh thu hoạt động tài chính", 
    "giá vốn hàng bán", "tổng cộng tài sản", "tổng tài sản", "vốn chủ sở hữu", "hàng tồn kho", 
    "tiền và các khoản tương đương tiền", "tương đương tiền", "tiền mặt", "chứng khoán kinh doanh", 
    "chi phí quản lý doanh nghiệp", "chi phí bán hàng", "chi phí tài chính", "chi phí lãi vay", "chi phí thuế", 
    "phải thu ngắn hạn", "phải thu dài hạn", "phải trả người bán", "người mua trả tiền trước", "vay và nợ", 
    "dự phòng rủi ro", "dự phòng", "lưu chuyển tiền thuần từ hoạt động kinh doanh", 
    "lưu chuyển tiền thuần từ hoạt động đầu tư", "lưu chuyển tiền thuần từ hoạt động tài chính",
    "vốn cổ phần", "thù lao", "tài sản ngắn hạn", "tài sản dài hạn", "nợ ngắn hạn", "nợ dài hạn", 
    "tổng nợ phải trả", "nợ phải trả", "nguyên giá", "giá trị còn lại", "chi phí xây dựng cơ bản dở dang", 
    "tài sản cố định hữu hình", "tài sản cố định vô hình", "thuế thu nhập doanh nghiệp", "thu nhập khác", 
    "chi phí khác", "lãi thuần", "lãi tiền gửi", "lãi vay", "cổ tức"
]

FILE_INDEX = {}
for f in list(RAW_DIR.rglob("*.txt")):
    doc_id = re.sub(r'_extracted$', '', f.stem)
    m_ticker = re.search(r'^([A-Z0-9]+)_', f.name)
    m_year = re.search(r'(\d{4})', f.name)
    if m_ticker and m_year:
        tk, yr = m_ticker.group(1).upper(), m_year.group(1)
        is_sep = "separate" in f.name.lower() or "rieng" in f.name.lower() or "me" in f.name.lower()
        req = "separate" if is_sep else "consolidated"
        FILE_INDEX[(tk, yr, req)] = (f, doc_id)
        if (tk, yr) not in FILE_INDEX: FILE_INDEX[(tk, yr)] = (f, doc_id)
        if tk not in FILE_INDEX: FILE_INDEX[tk] = (f, doc_id)

DOC_TABLES_CACHE = {}

def tokenize_vietnamese(text: str) -> List[str]:
    words = re.findall(r'\b[a-zA-ZÀ-ỹ0-9_]+\b', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]

def get_parsed_tables_for_doc(target_file: Path, doc_id: str) -> List[Dict[str, Any]]:
    if doc_id in DOC_TABLES_CACHE: return DOC_TABLES_CACHE[doc_id]
    tables_in_doc = []
    try:
        with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for line_idx, line in enumerate(lines):
            if "<table" not in line.lower(): continue
            t_match = re.search(r'<table.*?>.*?</table>', line, re.DOTALL | re.IGNORECASE)
            if not t_match: continue
            try:
                soup = BeautifulSoup(t_match.group(0), 'html.parser')
                t_elem = soup.find('table')
                if not t_elem: continue
                rows = [[re.sub(r'\s+', ' ', c.get_text()).strip() for c in tr.find_all(['td', 'th'])] for tr in t_elem.find_all('tr')]
                rows = [r for r in rows if r and any(r)]
                if not rows or len(rows[0]) < 2: continue

                max_cols = max(len(r) for r in rows)
                df = pd.DataFrame([r + [''] * (max_cols - len(r)) for r in rows])
                header_text = " ".join(df.iloc[0, :].astype(str)).lower()
                
                garbage_kws = ["mục lục", "thông tin chung", "hội đồng quản trị", "ban giám đốc", "giấy chứng nhận", "trang 1"]
                if any(k in header_text for k in garbage_kws): continue

                col0_txt = " ".join(df.iloc[:, 0].astype(str)).lower()
                tables_in_doc.append({
                    "line_1based": line_idx + 1, "df": df, "header": header_text, 
                    "tokens": tokenize_vietnamese(header_text + " " + col0_txt)
                })
            except Exception: pass
    except Exception: pass
    DOC_TABLES_CACHE[doc_id] = tables_in_doc
    return tables_in_doc

def build_strict_csv(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    if df is None or df.empty: 
        return pd.DataFrame([["Chỉ tiêu", 0.0], ["Tổng cộng", 0.0]], columns=["col_0", "col_1"])
    clean_rows = []
    for r in range(len(df)):
        label = str(df.iloc[r, 0]).strip()
        if len(df.columns) > 1 and len(label) <= 4: label = f"{label} {str(df.iloc[r, 1]).strip()}".strip()
        row_vals = [label]
        for c in range(1, len(df.columns)):
            v = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c])
            row_vals.append(float(v) if v else 0.0)
        clean_rows.append(row_vals)
    clean_df = pd.DataFrame(clean_rows)
    while clean_df.shape[1] < 2: clean_df[f"col_{clean_df.shape[1]}"] = 0.0
    clean_df.columns = [f"col_{i}" for i in range(clean_df.shape[1])]
    return clean_df

def detect_actual_financial_columns(df: pd.DataFrame, target_year: str, q_text: str) -> Tuple[int, int]:
    headers = [str(c).lower() for c in df.iloc[0, :].tolist()]
    prev_year = str(int(target_year) - 1) if target_year.isdigit() else "2021"
    q_lower = q_text.lower()
    is_asking_start = any(k in q_lower for k in ["đầu năm", "đầu kỳ", "01/01", "1/1"])
    
    valid_cols = []
    for c in range(1, len(df.columns)):
        if any(k in headers[c] for k in ["mã số", "thuyết minh", "tm", "stt", "chỉ tiêu"]): continue
        if sum(1 for r in range(1, min(10, len(df))) if abs(FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c]))) >= 1:
            valid_cols.append(c)

    c_curr, c_prev = -1, -1
    for c in valid_cols:
        if is_asking_start:
            if prev_year in headers[c] or any(k in headers[c] for k in ["đầu năm", "đầu kỳ", "01/01", "năm trước"]): c_curr = c
            if target_year in headers[c] or any(k in headers[c] for k in ["cuối năm", "cuối kỳ", "31/12", "năm nay"]): c_prev = c
        else:
            if target_year in headers[c] or any(k in headers[c] for k in ["cuối năm", "cuối kỳ", "31/12", "năm nay"]): c_curr = c
            if prev_year in headers[c] or any(k in headers[c] for k in ["đầu năm", "đầu kỳ", "01/01", "năm trước"]): c_prev = c

    if len(valid_cols) >= 2:
        if c_curr == -1: c_curr = valid_cols[0]
        if c_prev == -1: c_prev = valid_cols[1]
    elif len(valid_cols) == 1:
        c_curr = c_prev = valid_cols[0]

    return max(1, c_curr), max(1, c_prev)

def extract_metric_smart(tables: List[Dict[str, Any]], q_text: str, year: str, keywords: List[str]) -> Tuple[float, int, Optional[pd.DataFrame], int, int, int]:
    if not tables: return 0.0, 1, None, 0, 1, 1
    q_lower = q_text.lower()
    
    is_footnote_q = any(k in q_lower for k in ["ngành", "thù lao", "ông", "bà", "phạt", "chi tiết", "bên liên quan"])
    is_summary_q = any(k in q_lower for k in ["doanh thu", "tổng tài sản", "nợ phải trả", "vốn chủ sở hữu"]) and not is_footnote_q

    target_metric = next((m for m in sorted(FINANCIAL_METRICS, key=len, reverse=True) if m in q_lower), "")
            
    search_str = " ".join([kw.lower() for kw in keywords if len(kw) > 1])
    query_tokens = tokenize_vietnamese(q_text)
    corpus = [t["tokens"] for t in tables]
    bm25_scores = BM25Okapi(corpus).get_scores(query_tokens) if corpus else [0.0]*len(tables)

    best_val, best_line, best_df, best_r, best_c = 0.0, tables[0]["line_1based"], tables[0]["df"], 0, 1
    max_score, best_c_prev = -1000.0, 1

    for t_idx, t in enumerate(tables):
        df, bm25_sc = t["df"], bm25_scores[t_idx]
        
        table_bonus = 300.0 if (is_summary_q and t["line_1based"] <= 600) or (is_footnote_q and t["line_1based"] > 600) else -300.0
        c_curr, c_prev = detect_actual_financial_columns(df, year, q_text)

        for r in range(1, len(df)):
            row_lbl = f"{str(df.iloc[r, 0])} {str(df.iloc[r, 1]) if len(df.columns) > 1 else ''}".strip().lower()
            if len(row_lbl) < 3: continue

            val = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c_curr])
            if val == 0.0 and len(df) > 2: continue

            row_score = 0.0
            if target_metric:
                if target_metric == row_lbl: row_score = 1500.0
                elif target_metric in row_lbl: row_score = 1000.0
                else: row_score = sum(1 for kw in target_metric.split() if kw in row_lbl) * 80.0
            else:
                row_score = sum(1 for kw in search_str.split() if kw in row_lbl) * 60.0

            penalty = 0.0
            if "sau thuế" in q_lower and "trước thuế" in row_lbl: penalty -= 2000.0
            if "trước thuế" in q_lower and "sau thuế" in row_lbl: penalty -= 2000.0
            if "ngắn hạn" in q_lower and "dài hạn" in row_lbl: penalty -= 2000.0
            if "dài hạn" in q_lower and "ngắn hạn" in row_lbl: penalty -= 2000.0

            total_score = bm25_sc * 10.0 + row_score + table_bonus + penalty
            if total_score > max_score and row_score > 0:
                max_score, best_val, best_line, best_df, best_r, best_c, best_c_prev = total_score, val, t["line_1based"], df, r, c_curr, c_prev

    return best_val, best_line, best_df, best_r, best_c, best_c_prev

# ---------------------------------------------------------
# LLM ARBITRATOR (JSON EXTRACTION)
# ---------------------------------------------------------
def get_intent_json_from_llm(df: pd.DataFrame, q_text: str) -> dict:
    if df is None or df.empty: return {}
    
    df_preview = df.head(30).copy()
    df_preview.columns = [f"Col_{i}" for i in range(len(df_preview.columns))]
    table_preview = df_preview.to_markdown(index=True)

    prompt = f"""Phân tích báo cáo tài chính.
Câu hỏi: "{q_text}"

Bảng dữ liệu:
{table_preview}

YÊU CẦU: Trả về JSON gồm tọa độ dòng/cột chứa đáp án. LUÔN LẤY GIÁ TRỊ THÔ (RAW) TRONG BẢNG, KHÔNG quy đổi đơn vị tỷ/triệu.
- `row_index`: (int) Dòng.
- `col_index`: (int) Cột năm mục tiêu.
- `ref_col_index`: (int|null) Cột năm trước (chỉ dùng nếu hỏi biến động/tăng trưởng).
- `operation`: "value", "growth_pct", "growth_abs".
- `needs_abs`: (bool) true nếu hỏi về Chi phí, Nợ, Phạt.

Ví dụ: {{"row_index": 5, "col_index": 1, "ref_col_index": null, "operation": "value", "needs_abs": false}}
"""
    for model_name in ACTIVE_MODELS:
        try:
            completion = GROQ_CLIENT.chat.completions.create(
                model=model_name, messages=[{"role": "user", "content": prompt}], temperature=0.0, max_tokens=150
            )
            match = re.search(r'\{.*\}', completion.choices[0].message.content.strip(), re.DOTALL)
            if match: return json.loads(match.group(0))
        except Exception: continue
    return {}

def build_pandas_query_from_intent(intent: dict) -> str:
    if not intent or "row_index" not in intent or "col_index" not in intent: return ""
    r, c, c_prev = intent.get("row_index"), intent.get("col_index"), intent.get("ref_col_index")
    op, needs_abs = intent.get("operation", "value"), intent.get("needs_abs", False)
    
    query = ""
    if op == "growth_pct" and c_prev is not None:
        query = f"((float(df1.iloc[{r}, {c}]) - float(df1.iloc[{r}, {c_prev}])) / abs(float(df1.iloc[{r}, {c_prev}]))) * 100.0"
    elif op == "growth_abs" and c_prev is not None: query = f"(float(df1.iloc[{r}, {c}]) - float(df1.iloc[{r}, {c_prev}]))"
    else: query = f"float(df1.iloc[{r}, {c}])"

    return f"abs({query})" if needs_abs else query

def run():
    print("=" * 85)
    print("🚀 BẮT ĐẦU PIPELINE LLM ARBITRATOR + RAW VALUE (FINAL BOSS)...")
    print("=" * 85)
    t0 = time.time()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(TEST_FILE_PATH, "r", encoding="utf-8") as f: questions = [json.loads(l) for l in f if l.strip()]
    submission_data = []

    for idx, q in enumerate(questions, 1):
        q_id, q_text = q["id"], q["question"]
        q_lower = q_text.lower()

        detected_tickers = [tk for name, tk in FULL_COMPANY_MAP.items() if re.search(r'\b' + re.escape(name) + r'\b', q_lower)]
        raw_tickers = re.findall(r'\b[A-Z]{3}\b', q_text)
        tickers = detected_tickers + [t for t in raw_tickers if t not in detected_tickers]
        ticker = tickers[0] if tickers else "UNKNOWN"

        years = [int(y) for y in re.findall(r'\b(20\d\d)\b', q_text)]
        year = str(years[0]) if years else "2022"
        req_type = "separate" if any(k in q_lower for k in ["công ty mẹ", "riêng"]) else "consolidated"
        core_words = [w for w in re.findall(r'\b[a-zA-ZÀ-ỹ0-9_]+\b', q_lower) if w not in STOP_WORDS and len(w) > 1]
        
        matched_docs = []
        for tk in tickers:
            for yr in (years if years else [int(year)]):
                if (tk, str(yr), req_type) in FILE_INDEX: matched_docs.append(FILE_INDEX[(tk, str(yr), req_type)])
                elif (tk, str(yr)) in FILE_INDEX: matched_docs.append(FILE_INDEX[(tk, str(yr))])

        f1, d1 = matched_docs[0] if matched_docs else (None, f"{ticker}_financial_statements_{year}_{req_type}")
        t1 = get_parsed_tables_for_doc(f1, d1) if f1 else []
        
        # 1. TÌM BẢNG BẰNG BM25 + SPATIAL ROUTING
        v1, l1, df1_raw, r1, c1, c_prev = extract_metric_smart(t1, q_text, year, core_words)
        c_df1 = build_strict_csv(df1_raw)
        
        is_growth_pct = any(k in q_lower for k in ["tăng trưởng", "tăng bao nhiêu %", "giảm bao nhiêu %", "tốc độ tăng", "% tăng"])
        is_growth_abs = any(k in q_lower for k in ["tăng bao nhiêu", "giảm bao nhiêu", "chênh lệch", "biến động", "hiệu số", "lớn hơn", "thấp hơn"]) and not is_growth_pct
        needs_abs = any(k in q_lower for k in ["chi phí", "dự phòng", "nợ", "phải trả", "lỗ", "cầm cố", "lãi vay", "thù lao", "thuế", "phạt"])
        if "lợi nhuận" in q_lower and "lỗ" not in q_lower: needs_abs = False

        # 2. XÂY DỰNG RAW QUERY (BASELINE)
        if is_growth_pct and c1 != c_prev and df1_raw is not None:
            fallback_query = f"((float(df1.iloc[{r1}, {c1}]) - float(df1.iloc[{r1}, {c_prev}])) / abs(float(df1.iloc[{r1}, {c_prev}]))) * 100.0"
        elif is_growth_abs and c1 != c_prev and df1_raw is not None:
            fallback_query = f"(float(df1.iloc[{r1}, {c1}]) - float(df1.iloc[{r1}, {c_prev}]))"
        else:
            fallback_query = f"float(df1.iloc[{r1}, {c1}])"

        if needs_abs: fallback_query = f"abs({fallback_query})"

        try: fallback_val = float(eval(fallback_query, {"__builtins__": None}, {"df1": c_df1, "abs": abs, "float": float}))
        except Exception: fallback_val, fallback_query = 0.0, "0.0"

        # 3. LLM ARBITRATOR (KÉO ĐIỂM)
        final_query = fallback_query
        final_val = fallback_val
        engine = "CODE"

        if df1_raw is not None and not df1_raw.empty:
            intent_json = get_intent_json_from_llm(df1_raw, q_text)
            llm_query = build_pandas_query_from_intent(intent_json)
            if llm_query:
                try:
                    local_env = {"df1": c_df1, "abs": abs, "float": float}
                    llm_val = float(eval(llm_query, {"__builtins__": None}, local_env))
                    if llm_val != fallback_val:
                        final_query = llm_query
                        final_val = llm_val
                        engine = " LLM"
                except Exception: pass
        
        # Ngủ nhẹ chống Rate Limit
        time.sleep(1.2)

        csv1_name = f"{d1}_table_{l1}.csv"
        c_df1.to_csv(DATA_DIR / csv1_name, index=False)

        valid_docs = [d for d in [doc[1] for doc in matched_docs] if "financial_statements" in d]
        if not valid_docs: valid_docs = [d1]

        submission_data.append({
            "id": int(q_id), "question": str(q_text), "answer": float(final_val),
            "relevant_docs": valid_docs, "relevant_tables": [f"{d1}|{l1}"],
            "evidence": [{"variable": "df1", "csv_path": f"data/{csv1_name}"}],
            "pandas_query": str(final_query)
        })

        if idx % 20 == 0 or idx == len(questions):
            print(f"[{idx:04d}/{len(questions):04d}] [{engine}] {ticker} | Doc: {d1} | KQ: {final_val:,.2f}")

    submission_data.sort(key=lambda x: x["id"])
    with open(OUT_DIR / "submission.json", "w", encoding="utf-8") as f:
        json.dump(submission_data, f, ensure_ascii=False, indent=2)
    shutil.make_archive(str(ROOT_DIR / "FINAL_PIPELINE_SUBMISSION"), 'zip', str(OUT_DIR))
    
    elapsed = time.time() - t0
    print("=" * 85)
    print(f"🎉 HOÀN TẤT TOÀN BỘ TRONG {elapsed:.2f} GIÂY!")
    print("=" * 85)

if __name__ == "__main__":
    run()