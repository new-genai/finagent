import requests
import json

url = "http://localhost:8000/api/chat"

cases = [
    "doanh thu vnm 2022",
    "VNM 2022",
    "Doanh thu của VNM năm 2023 là bao nhiêu?",
    "vnm doanh thu 2022",
    "xin chào",
    "cảm ơn",
    "có hỏi doanh thu đâu",
    "VNM",
    "doanh thu",
    "tính tăng trưởng doanh thu VNM 2022 2023"
]

results = []
for q in cases:
    try:
        res = requests.post(url, json={"question": q, "history": []})
        if res.status_code == 200:
            data = res.json()
            results.append({
                "Q": q,
                "A": data.get("answer"),
                "ExecutedPandas": bool(data.get("thought_process"))
            })
        else:
            results.append({"Q": q, "ERROR": res.text})
    except Exception as e:
        results.append({"Q": q, "ERROR": str(e)})

with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
