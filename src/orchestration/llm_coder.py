import json
import re
import requests

def ask_qwen14b_for_pandas(question, df_markdown, year):
    prompt = f"""Bạn là chuyên gia lập trình Python Pandas tài chính.
Câu hỏi: {question}
Bảng dữ liệu trích xuất (được nạp vào biến df1):
{df_markdown}

Nhiệm vụ:
Viết 01 biểu thức Python pandas (gán kết quả vào 'result' hoặc trả về 1 dòng) để tính toán đúng theo câu hỏi.
Ví dụ: 
- Tính tăng trưởng: (float(df1.iloc[1, 2]) - float(df1.iloc[1, 1])) / abs(float(df1.iloc[1, 1])) * 100.0
- Lấy 1 ô: float(df1.iloc[5, 1]) * 1e-6

Chỉ trả về JSON định dạng sau:
{{
    "pandas_query": "<biểu_thức_python_tính_toán>",
    "answer": <kết_quả_float>
}}
"""
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "qwen2.5:14b",
            "prompt": prompt,
            "format": "json",
            "stream": False
        }, timeout=15)
        res_json = json.loads(res.json()["response"])
        return res_json.get("pandas_query"), float(res_json.get("answer", 0.0))
    except Exception:
        return None, None