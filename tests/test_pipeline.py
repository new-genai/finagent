import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

def run_test(question: str):
    print(f"\n{'='*50}")
    print(f"QUESTION: {question}")
    print(f"{'='*50}")
    
    start_time = time.time()
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={"question": question},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        
        print("\n--- PANDAS CODE ---")
        print(data.get("thought_process", ""))
        
        print("\n--- FINAL ANSWER ---")
        print(data.get("answer", ""))
        
        print(f"\nTime taken: {time.time() - start_time:.2f} seconds")
        print(f"Tables used: {data.get('tables_used', [])}")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_questions = [
        "Doanh thu VNM 2023 là bao nhiêu?",
        "Lợi nhuận HPG 2022",
        "Tổng tài sản FPT",
        "Biên lợi nhuận MWG"
    ]
    
    print("Running E2E Pipeline Tests...")
    for q in test_questions:
        run_test(q)
