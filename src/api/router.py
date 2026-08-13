import logging
import re
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.schemas.api import (
    RetrieveRequest, RetrieveResponse, RetrievedTable,
    ExecuteRequest, ExecuteResponse,
    ChatRequest, ChatResponse,
    SubmissionRequest, DatasetStatsResponse
)
from src.core.config import settings
from .deps import (
    get_hybrid_retriever, 
    get_pandas_executor, 
    get_llm_service, 
    get_submission_generator, 
    get_db_service,
    get_table_loader
)

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

@router.get("/health")
def health_check():
    """Kiểm tra trạng thái server."""
    return {"status": "ok", "version": settings.APP_VERSION}

@router.get("/dataset/statistics", response_model=DatasetStatsResponse)
def get_statistics(db = Depends(get_db_service)):
    """Lấy thống kê sơ bộ về Dataset."""
    return DatasetStatsResponse(
        total_files=0,
        total_tables=0,
        companies=["VNM", "FPT"],
        years=["2022", "2023"]
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
def chat_end_to_end(req: ChatRequest, 
                    retriever = Depends(get_hybrid_retriever),
                    table_loader = Depends(get_table_loader),
                    llm = Depends(get_llm_service),
                    executor = Depends(get_pandas_executor)):
    """
    Luồng chạy End-to-End theo chuẩn Text2Pandas.
    Các bước: Question -> Analyze Intent -> Missing Data Check -> Hybrid Retrieve -> Load DataFrames -> Build Context -> LLM Generate -> Pandas Execute -> Validation -> Natural Response -> Answer.
    """
    try:
        logger.info(f"--- BẮT ĐẦU PIPELINE CHO CÂU HỎI: '{req.question}' ---")
        
        # Bước 1: Analyze Intent and Extract Entities
        parsed_intent = llm.analyze_intent_and_extract(req.question, req.history)
        intent = parsed_intent.get("intent", "financial_query")
        
        if intent in ["conversation", "clarification", "unsupported"]:
            logger.info(f"Routed as '{intent}'. Returning direct answer.")
            return ChatResponse(
                answer=parsed_intent.get("direct_answer", "Xin lỗi, tôi chưa hiểu rõ ý bạn."),
                tables_used=[],
                thought_process=""
            )
            
        rewritten_question = parsed_intent.get("rewritten_query", req.question)
        requested_companies = set(parsed_intent.get("tickers", []))
        requested_years = set(parsed_intent.get("years", []))
        
        # Kiểm tra missing data
        missing_answer = _missing_data_answer(requested_companies, requested_years, retriever)
        if missing_answer:
            return missing_answer
        
        # Dùng cleaned_question để tìm kiếm (tránh nhiễu từ 'năm' hoặc ticker)
        cleaned_question = rewritten_question.lower()
        for c in requested_companies:
            cleaned_question = re.sub(rf"\b{c.lower()}\b", "", cleaned_question)
        for y in requested_years:
            cleaned_question = re.sub(rf"\b{y}\b", "", cleaned_question)
        cleaned_question = re.sub(rf"\bnăm\b", "", cleaned_question).strip()
        
        # Lấy toàn bộ index sau đó filter để đảm bảo không miss bất kỳ bảng nào
        raw_tables = retriever.retrieve(cleaned_question, top_k=3000)
        
        # Lọc các bảng đúng với company và year được yêu cầu
        tables = []
        for t in raw_tables:
            if requested_companies and str(t.company).upper() not in requested_companies:
                continue
            if requested_years and str(t.year) not in requested_years:
                continue
            tables.append(t)
            
        tables = tables[:settings.TOP_K_RETRIEVAL]
        table_ids = [t.table_id for t in tables]
        logger.info(f"[Retrieval] Đã tìm thấy {len(tables)} bảng sau khi lọc: {table_ids}")
        
        # Bước 2: Nạp DataFrames (Table Loader)
        dfs = table_loader.load_dataframes(tables)
        logger.info(f"[Loader] Đã load {len(dfs)} DataFrames vào Sandbox.")
        
        # Bước 3: Tạo Prompt Context
        context_str = llm.context_builder.build(tables)
        logger.info(f"[ContextBuilder] Đã tạo context cho Prompt.")
        
        # Bước 4: LLM sinh code dựa trên Context
        code = llm.generate_pandas_code(rewritten_question, context_str)
        
        # Bước 5: Đưa code vào Executor chạy độc lập với Timeout
        success, output = executor.execute(code, dfs)
        logger.info(f"[Execution] Kết quả chạy code: Success={success}")
        
        # Bước 6: Validate and create natural response
        if success:
            output_str = str(output).strip()
            if not output_str or output_str == "None" or output_str == "Empty DataFrame" or "không tìm thấy" in output_str.lower():
                natural_answer = "Dựa trên dữ liệu hiện có, tôi không tìm thấy thông tin cụ thể để trả lời câu hỏi này. Có thể chỉ tiêu này không có trong năm bạn yêu cầu hoặc khác tên gọi trong báo cáo."
            else:
                natural_answer = llm.generate_natural_response(rewritten_question, output, req.history)
            return ChatResponse(answer=natural_answer, thought_process=code, tables_used=table_ids)
        else:
            return ChatResponse(answer=f"Lỗi khi thực thi code phân tích: {output}", thought_process=code, tables_used=table_ids)
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submission")
def generate_submission(req: SubmissionRequest, generator = Depends(get_submission_generator)):
    """Tạo file submission.json đúng chuẩn format BTC yêu cầu."""
    generator.generate({"message": "This is a mock submission"}, settings.BASE_DIR / "submission.json")
    return {"status": "success", "message": "Submission file created."}
