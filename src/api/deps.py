import logging
from functools import lru_cache
from pathlib import Path

from src.core.config import settings
from src.llm.context_builder import ContextBuilder
from src.llm.prompt_builder import PromptBuilder
from src.llm.service import LLMService
from src.database.supabase_service import SupabaseService
from src.execution.table_loader import TableLoader
from src.execution.pandas_executor import PandasExecutor

logger = logging.getLogger(__name__)

@lru_cache()
def get_db_service() -> SupabaseService:
    return SupabaseService()

@lru_cache()
def get_table_loader() -> TableLoader:
    return TableLoader()

@lru_cache()
def get_pandas_executor() -> PandasExecutor:
    return PandasExecutor(timeout_sec=settings.PANDAS_EXECUTION_TIMEOUT_SEC)

from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.embedding.service import EmbeddingService

@lru_cache()
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

@lru_cache()
def get_hybrid_retriever() -> BM25Retriever:
    """Nạp BM25 Retriever thuần túy để tiết kiệm chi phí và chạy ngay không cần embedding."""
    index_file = settings.INDEX_DIR / "bm25.pkl"
    bm25 = BM25Retriever()
    if index_file.exists():
        bm25.load(index_file)
    else:
        logger.warning(f"Chưa tìm thấy index tại {index_file}.")
        
    return bm25

@lru_cache()
def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()

@lru_cache()
def get_context_builder() -> ContextBuilder:
    return ContextBuilder(table_loader=get_table_loader())

@lru_cache()
def get_llm_service() -> LLMService:
    return LLMService(
        prompt_builder=get_prompt_builder(),
        context_builder=get_context_builder()
    )