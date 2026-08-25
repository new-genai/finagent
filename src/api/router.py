import logging
import re
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from simpleeval import simple_eval
from src.schemas.api import ChatRequest, ChatResponse, Evidence, DatasetStatsResponse, RetrieveRequest, RetrieveResponse, ExecuteRequest, ExecuteResponse
from src.core.config import settings
from .deps import get_hybrid_retriever, get_pandas_executor, get_llm_service, get_table_loader
from src.agents.base import QueryPlan, ExecutionStep
import concurrent.futures

logger = logging.getLogger(__name__)
router = APIRouter()

def _get_index_docs(retriever) -> List[Dict[str, Any]]:
    bm25 = getattr(retriever, "bm25", None)
    docs = getattr(bm25, "doc_store", None)
    return docs or []


def _missing_data_answer(requested_companies: set[str], requested_years: set[str], retriever) -> ChatResponse | None:
    docs = _get_index_docs(retriever)
    if not docs:
        return ChatResponse(
            answer="Backend chưa có dữ liệu index để trả lời. Hãy chạy lại bước build metadata/index.",
            tables_used=[],
        )

    available_companies = {str(doc.get("company", "")).upper() for doc in docs if doc.get("company")}
    unknown_companies = requested_companies - available_companies
    available_years = {str(doc.get("year", "")) for doc in docs if doc.get("year")}

    if unknown_companies:
        tickers = ", ".join(sorted(unknown_companies))
        return ChatResponse(
            answer=f"Hiện index chưa có dữ liệu cho mã {tickers}, nên mình không thể trả lời chính xác câu hỏi này.",
            tables_used=[],
        )

    scoped_docs = [
        doc for doc in docs
        if not requested_companies or str(doc.get("company", "")).upper() in requested_companies
    ]

    if requested_years:
        scoped_years = {str(doc.get("year", "")) for doc in scoped_docs if doc.get("year")}
        missing_years = requested_years - scoped_years
        if missing_years:
            years = ", ".join(sorted(missing_years))
            available = ", ".join(sorted(scoped_years or available_years)) or "chưa rõ"
            return ChatResponse(
                answer=f"Hiện dữ liệu index chưa có năm {years}. Các năm đang có: {available}.",
                tables_used=[],
            )

    return None


def _extract_table_dimensions(table_name: str) -> tuple[str | None, str | None]:
    match = re.match(r"^([A-Z0-9]{2,10})_(\d{4})_", table_name.upper())
    if not match:
        return None, None
    return match.group(1), match.group(2)

@router.get("/health")
def health_check():
    """Kiểm tra trạng thái server."""
    return {"status": "ok", "version": settings.APP_VERSION}

@router.get("/dataset/statistics", response_model=DatasetStatsResponse)
def get_statistics(db = Depends(get_db_service)):
    """Lấy thống kê sơ bộ về Dataset."""
    table_names: list[str] = []

    try:
        if db:
            rows = db.query("SHOW TABLES")
            if hasattr(rows, "iloc"):
                table_names = [str(value) for value in rows.iloc[:, 0].tolist()]
            else:
                table_names = [str(row[0]) for row in rows]
    except Exception as e:
        logger.warning(f"Could not read DuckDB table statistics: {e}")

    if not table_names:
        csv_dir = settings.BASE_DIR / "data" / "processed" / "csv"
        if csv_dir.exists():
            table_names = [path.stem for path in csv_dir.glob("*.csv")]

    company_counts: dict[str, int] = {}
    year_counts: dict[str, int] = {}
    report_keys: set[tuple[str, str]] = set()

    for table_name in table_names:
        company, year = _extract_table_dimensions(table_name)
        if company:
            company_counts[company] = company_counts.get(company, 0) + 1
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1
        if company and year:
            report_keys.add((company, year))

    return DatasetStatsResponse(
        total_files=len(report_keys),
        total_tables=len(table_names),
        companies=sorted(company_counts),
        years=sorted(year_counts),
        company_table_counts=dict(sorted(company_counts.items())),
        year_table_counts=dict(sorted(year_counts.items()))
    )

@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_tables(req: RetrieveRequest, retriever = Depends(get_hybrid_retriever)):
    """Tìm kiếm các bảng phù hợp với câu hỏi bằng Hybrid Search."""
    if not retriever:
        raise HTTPException(status_code=500, detail="Retriever not initialized.")
        
    try:
        tables = retriever.retrieve(req.question, top_k=settings.TOP_K_RETRIEVAL)
        return RetrieveResponse(tables=tables)
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=ExecuteResponse)
def execute_pandas_code(req: ExecuteRequest, executor = Depends(get_pandas_executor)):
    """Thực thi trực tiếp code Pandas do LLM sinh ra."""
    if not executor:
        raise HTTPException(status_code=500, detail="Executor not initialized.")
        
    success, output = executor.execute(req.code)
    
    if success:
        return ExecuteResponse(success=True, result=output)
    else:
        return ExecuteResponse(success=False, error=output)

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
            step_logs = [f"\n>> ĐANG CHẠY {step.step_id.upper()}: Tìm '{step.metric_intent}'"]
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
                final_pandas_query += f"\n# --- {s_id} ---\n{s_code}\n"

        final_result = global_state.get("step_1") if not plan.is_complex else None
        if plan.is_complex and plan.final_formula and all(v is not None for v in global_state.values()):
            try:
                final_result = simple_eval(plan.final_formula, names=global_state)
            except: pass
                
        combined_thought = "=== TRACE DAG ENGINE ===\n" + "\n".join(trace_logs)
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
