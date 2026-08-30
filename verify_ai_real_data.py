import json
import re
import asyncio
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
from bs4 import BeautifulSoup
import pandas as pd
from openai import AsyncOpenAI

from src.metadata.normalizer import FinancialDataCleaner

ROOT_DIR = Path(__file__).resolve().parent
RAW_DIR = ROOT_DIR / "data" / "raw"

OPENROUTER_API_KEY = ""
MODEL_NAME = "qwen/qwen-2.5-7b-instruct"

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    timeout=30.0
)

FILE_INDEX = {}
for f in RAW_DIR.rglob("*.txt"):
    m_ticker = re.search(r'^([A-Z0-9]+)_', f.name)
    m_year = re.search(r'(\d{4})', f.name)
    if m_ticker and m_year:
        tk = m_ticker.group(1).upper()
        yr = m_year.group(1)
        is_sep = "separate" in f.name.lower() or "rieng" in f.name.lower() or "me" in f.name.lower()
        req = "separate" if is_sep else "consolidated"
        FILE_INDEX[(tk, yr, req)] = f

def build_strict_csv(df: pd.DataFrame) -> pd.DataFrame:
    clean_rows = []
    for r in range(len(df)):
        label = str(df.iloc[r, 0]).strip()
        if len(df.columns) > 1 and len(label) <= 4: 
            label = f"{label} {str(df.iloc[r, 1]).strip()}".strip()
        row_vals = [label]
        for c in range(1, len(df.columns)):
            v = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c])
            if 31121990 <= abs(v) <= 31122035: v = 0.0
            row_vals.append(float(v))
        clean_rows.append(row_vals)
    clean_df = pd.DataFrame(clean_rows)
    clean_df.columns = [f"col_{i}" for i in range(clean_df.shape[1])]
    return clean_df

# ĐỊNH VỊ BẢNG CHÍNH XÁC Ở ĐẦU FILE (DÒNG 100 - 550)
def get_primary_statement_table(file_path: Path, q_text: str) -> Tuple[pd.DataFrame, int, str]:
    q_lower = q_text.lower()
    if any(k in q_lower for k in ["doanh thu", "lợi nhuận", "giá vốn", "chi phí", "thu nhập"]):
        target_type = "IS"
    elif any(k in q_lower for k in ["lưu chuyển", "tiền thuần"]):
        target_type = "CF"
    else:
        target_type = "BS"

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines[:600]):  # Chỉ quét 600 dòng đầu (BCTC chính)
        if "<table" in line.lower():
            soup = BeautifulSoup(line, 'html.parser')
            t_elem = soup.find('table')
            if not t_elem: continue
            rows = []
            for tr in t_elem.find_all('tr'):
                cells = [re.sub(r'\s+', ' ', c.get_text()).strip() for c in tr.find_all(['td', 'th'])]
                if cells and any(cells): rows.append(cells)
            if len(rows) > 3:
                max_cols = max(len(r) for r in rows)
                df = pd.DataFrame([r + [''] * (max_cols - len(r)) for r in rows])
                full_text = " ".join(df.astype(str).values.flatten()).lower()
                
                # Loại trừ bảng nhân sự và bảng biến động vốn
                if any(k in full_text for k in ["hội đồng quản trị", "ban điều hành", "số dư tại ngày", "trả cổ tức bằng"]):
                    continue

                if target_type == "IS" and any(k in full_text for k in ["doanh thu thuần", "lợi nhuận gộp", "kết quả hoạt động kinh doanh"]):
                    return build_strict_csv(df), idx + 1, "Báo cáo Kết quả Kinh doanh (IS)"
                elif target_type == "BS" and any(k in full_text for k in ["tổng cộng tài sản", "tài sản ngắn hạn"]):
                    return build_strict_csv(df), idx + 1, "Bảng Cân đối Kế toán (BS)"
                elif target_type == "CF" and any(k in full_text for k in ["lưu chuyển tiền thuần"]):
                    return build_strict_csv(df), idx + 1, "Báo cáo Lưu chuyển Tiền tệ (CF)"

    return pd.DataFrame(), 0, "Không tìm thấy"

async def test_single_question(q_id: int, ticker: str, year: int, q_text: str):
    print("\n" + "=" * 95)
    print(f"📌 [TEST CÂU {q_id}] {q_text}")
    print("=" * 95)
    
    file_path = FILE_INDEX.get((ticker, str(year), "consolidated")) or FILE_INDEX.get((ticker, str(year), "separate"))
    if not file_path:
        print("❌ Không tìm thấy file BCTC!")
        return

    clean_df, line_num, statement_name = get_primary_statement_table(file_path, q_text)
    if clean_df.empty:
        print("❌ Không tìm thấy bảng phù hợp!")
        return

    print(f"📊 BẢNG KẾ TOÁN CHUẨN: {statement_name} ({file_path.name} | Dòng {line_num})")

    # Hiển thị tường minh các cột số thực tế cho AI
    rows_text = []
    for r in range(len(clean_df)):
        lbl = clean_df.iloc[r, 0]
        # Lọc các cột có số thực tế lớn (bỏ qua cột mã số/thuyết minh nhỏ)
        num_cols = [c for c in range(1, len(clean_df.columns)) if abs(clean_df.iloc[r, c]) > 1000]
        if num_cols:
            col_desc = " | ".join([f"Cột {c}: {clean_df.iloc[r, c]:,.0f}" for c in num_cols])
            rows_text.append(f"- Dòng {r:02d} [{lbl}]: {col_desc}")

    prompt = f"""Bạn là Chuyên gia Kế toán Trưởng. Hãy đọc bảng BCTC và lập biểu thức Python `pandas_query` trả lời câu hỏi:

[DANH SÁCH CÁC DÒNG SỐ LIỆU TÀI CHÍNH]
{chr(10).join(rows_text)}

[CÂU HỎI]
{q_text}

[QUY TẮC BẮT BUỘC]
1. Chỉ dùng cú pháp: `float(df1.iloc[row, col])` và toán tử (+, -, *, /).
2. Tra cứu giá trị 1 dòng: Lấy đúng dòng tổng/chỉ tiêu yêu cầu (ví dụ dòng Tổng tài sản, Doanh thu thuần).
   Cú pháp: `float(df1.iloc[r, c])`
3. Tính tăng trưởng %: `(float(df1.iloc[r, c_nay]) - float(df1.iloc[r, c_truoc])) / float(df1.iloc[r, c_truoc]) * 100.0`
   (LƯU Ý: Mẫu số `c_truoc` PHẢI là cột có giá trị tiền lớn của năm trước, TUYỆT ĐỐI KHÔNG chọn cột mã số hay cột bằng 0).

Trả về DUY NHẤT 1 JSON:
{{"pandas_query": "<biểu thức>", "thought": "<giải thích ngắn gọn>"}}"""

    res = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    data = json.loads(res.choices[0].message.content)
    query = data.get("pandas_query", "")
    thought = data.get("thought", "")

    try:
        val = float(eval(query, {"df1": clean_df, "float": float, "abs": abs}))
        print(f"\n🧠 AI SUY LUẬN : {thought}")
        print(f"⚙️ PANDAS QUERY: {query}")
        print(f"🎯 KẾT QUẢ TÍNH: {val:,.2f}")
        print("✅ TÌNH TRẠNG   : THỰC THI THÀNH CÔNG 100%")
    except Exception as e:
        print(f"\n❌ LỖI THỰC THI SANDBOX: {e}")

async def main():
    await test_single_question(1, "HPG", 2021, "Doanh thu thuần của HPG năm 2021 là bao nhiêu?")
    await test_single_question(2, "VNM", 2024, "Lợi nhuận gộp của VNM năm 2024 tăng trưởng bao nhiêu % so với năm trước?")
    await test_single_question(3, "VIC", 2022, "Tổng tài sản của Vingroup năm 2022 là bao nhiêu?")

if __name__ == "__main__":
    asyncio.run(main())