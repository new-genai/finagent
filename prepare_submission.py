import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 1. CẬP NHẬT SCHEMA API: Thêm pandas_query và evidence để khớp định dạng nộp bài
schema_code = """from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional

class RetrievedTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    table_id: str
    duckdb_table: str = ""
    company: str
    year: str
    score: float = 0.0
    columns: List[str] = Field(default_factory=list)
    dataframe: Any = None

class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question.")
    history: Optional[List[Dict[str, Any]]] = Field(default=None)

class Evidence(BaseModel):
    variable: str
    csv_path: str

class ChatResponse(BaseModel):
    answer: str
    thought_process: Optional[str] = None
    relevant_docs: List[str] = []
    relevant_tables: List[str] = []
    evidence: List[Evidence] = []
    pandas_query: str = ""
"""
(ROOT / "src" / "schemas" / "api.py").write_text(schema_code, encoding="utf-8")

# 2. XÓA BỎ INTERCEPTOR TRONG ROUTER VÀ TRẢ VỀ ĐÚNG CHUẨN JSON CỦA BTC
router_code = """import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from simpleeval import simple_eval
from src.schemas.api import ChatRequest, ChatResponse, Evidence
from src.core.config import settings
from .deps import get_hybrid_retriever, get_pandas_executor, get_llm_service, get_table_loader
from src.agents.base import QueryPlan, ExecutionStep
import concurrent.futures

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_end_to_end(
    req: ChatRequest, 
    retriever=Depends(get_hybrid_retriever), 
    table_loader=Depends(get_table_loader), 
    llm=Depends(get_llm_service), 
    executor=Depends(get_pandas_executor)
):
    try:
        # ĐÃ XÓA BỎ LỚP INTERCEPTOR GÁN CỨNG (HARDCODE) - TUÂN THỦ TUYỆT ĐỐI LUẬT BTC
        logger.info(f"--- BẮT ĐẦU DAG ENGINE: '{req.question}' ---")
        plan_dict = llm.decompose_query(req.question)
        plan = QueryPlan(**plan_dict)
        
        company = plan.company
        year = plan.year
        global_state: Dict[str, Any] = {}
        
        all_relevant_docs = set()
        all_relevant_tables = set()
        all_evidence = []
        final_pandas_query = ""
        trace_logs = []
        
        steps = plan.steps
        if not plan.is_complex or not steps:
            steps = [ExecutionStep(step_id="step_1", metric_intent=req.question, sub_queries=plan.sub_queries if plan.sub_queries else [req.question])]
            
        def process_step(step):
            step_logs = [f"\\n>> ĐANG CHẠY {step.step_id.upper()}: Tìm '{step.metric_intent}'"]
            sq_list = step.sub_queries if step.sub_queries else [step.metric_intent]
            selected_tables = []
            seen_table_ids = set()

            for sq in sq_list:
                sub_results = retriever.retrieve_single(sub_query=sq, company=company, year=year, top_k=15)
                for t in sub_results:
                    if t.table_id not in seen_table_ids:
                        seen_table_ids.add(t.table_id)
                        selected_tables.append(t)

            dfs = table_loader.load_dataframes(selected_tables)
            context_str = llm.context_builder.build(selected_tables, metric_intent=step.metric_intent)
            
            # Lưu vết evidence cho BTC
            step_evidence = []
            for t_id, df in dfs.items():
                all_relevant_docs.add(t_id.rsplit('_page', 1)[0]) # Cắt đuôi để ra id báo cáo
                all_relevant_tables.add(f"{t_id}|0") # Tạm dùng 0 do ko có số dòng OCR
                step_evidence.append(Evidence(variable=f"dfs['{t_id}']", csv_path=f"data/{t_id}.csv"))

            step_plan = plan.model_dump()
            code = llm.generate_pandas_code_dynamic(step.metric_intent, step_plan, context_str)
            
            step_success = False
            extracted_value = None

            for attempt in range(2):
                success, output = executor.execute(code, dfs)
                if success and isinstance(output, dict) and output.get("value") is not None:
                    extracted_value = output["value"]
                    step_success = True
                    step_logs.append(f"   [Thử {attempt + 1}] THÀNH CÔNG! Trích xuất: {extracted_value}")
                    break
                
                if success and output is not None and not isinstance(output, dict) and not str(output).startswith("ERROR:") and str(output) not in ["None", "nan", "NaN", ""]:
                    extracted_value = output
                    step_success = True
                    break
                    
                error_msg = str(output) if not success else "Giá trị rỗng."
                if attempt < 1:
                    code = llm.fix_pandas_code(code, error_msg, step.metric_intent, context_str)

            final_val = float(extracted_value) if step_success and extracted_value is not None else None
            return step.step_id, final_val, step_logs, step_evidence, code

        with concurrent.futures.ThreadPoolExecutor() as thread_pool:
            futures = [thread_pool.submit(process_step, step) for step in steps]
            for future in concurrent.futures.as_completed(futures):
                s_id, val, s_logs, s_ev, s_code = future.result()
                global_state[s_id] = val
                trace_logs.extend(s_logs)
                all_evidence.extend(s_ev)
                final_pandas_query += f"\\n# --- {s_id} ---\\n{s_code}\\n"

        final_result = global_state.get("step_1") if not plan.is_complex else None
        if plan.is_complex and plan.final_formula and all(v is not None for v in global_state.values()):
            try:
                final_result = simple_eval(plan.final_formula, names=global_state)
            except: pass
                
        combined_thought = "=== TRACE DAG ENGINE ===\\n" + "\\n".join(trace_logs)
        ans = llm.generate_natural_response(req.question, str(final_result), req.history) if final_result is not None else llm.generate_cot_fallback(req.question, "")
        
        return ChatResponse(
            answer=ans, 
            thought_process=combined_thought,
            relevant_docs=list(all_relevant_docs),
            relevant_tables=list(all_relevant_tables),
            evidence=all_evidence,
            pandas_query=final_pandas_query.strip()
        )
            
    except Exception as e:
        logger.error(f"Lỗi Chat Pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
"""
(ROOT / "src" / "api" / "router.py").write_text(router_code, encoding="utf-8")

# 3. TẠO SCRIPT XUẤT SUBMISSION THEO ĐÚNG CHUẨN BTC
submission_code = """import json
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
"""
(ROOT / "generate_submission.py").write_text(submission_code, encoding="utf-8")

print("✅ ĐÃ CHUẨN HÓA HỆ THỐNG ĐỂ NỘP BÀI THỰC TẾ!")