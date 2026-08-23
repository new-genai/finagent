import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/chat"

# Những câu hỏi KHÔNG NẰM TRONG BENCHMARK để kiểm tra năng lực thực sự của DAG Engine
real_questions = [
    "Doanh thu năm 2022 của Vinamilk (VNM) là bao nhiêu?",
    "Tổng tài sản của ngân hàng ACB năm 2023 là bao nhiêu?",
    "Lợi nhuận sau thuế của Hòa Phát (HPG) năm 2022?"
]

print("="*80)
print("🚀 BẮT ĐẦU KIỂM THỬ NĂNG LỰC THỰC TẾ CỦA FINAGENT DAG ENGINE")
print("="*80)

for idx, q in enumerate(real_questions, 1):
    print(f"\n[Câu hỏi {idx}]: {q}")
    print("⏳ Đang suy nghĩ và xử lý dữ liệu...")
    
    start_time = time.time()
    try:
        response = requests.post(API_URL, json={"question": q}, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Xong trong {elapsed:.2f}s!")
            print(f"💰 TRẢ LỜI: {data.get('answer')}")
            print("\n💻 DẤU VẾT DAG ENGINE (Thought Process):")
            print("-" * 50)
            print(data.get('thought_process'))
            print("-" * 50)
        else:
            print(f"❌ LỖI API ({response.status_code}): {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI KẾT NỐI: {e}")