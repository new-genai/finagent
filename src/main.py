import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.router import router
import src.api.deps as deps

# Import toàn bộ các Module thuộc Clean Architecture
from src.database.duckdb_service import DuckDBService
from src.retrieval import FAISSIndex, BM25Retriever, HybridRetriever
from src.embedding.service import EmbeddingService
from src.executor.pandas_executor import PandasExecutor
from src.services.table_loader import TableLoader
from src.llm.service import LLMService
from src.llm.prompt_builder import PromptBuilder
from src.llm.context_builder import ContextBuilder
from src.submission.generator import SubmissionGenerator

# Thiết lập hệ thống Logging chuẩn xác
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Sự kiện Lifespan: Khởi tạo tất cả các Service hạng nặng 1 lần duy nhất khi Server khởi động.
    Điều này giúp Endpoint chạy cực kỳ nhanh chóng.
    """
    logger.info("🚀 Starting up NewGenAI Financial Agent Backend...")
    
    # 1. Khởi tạo Database (DuckDB)
    db_path = Path(settings.DB_PATH)
    db_service = DuckDBService(str(db_path), read_only=db_path.exists())
    
    # Load thực tế từ finagent.db
    if db_path.exists():
        logger.info(f"Loading DuckDB from {db_path}")
    else:
        logger.warning(f"Database {db_path} not found. Please run the data ingestion pipeline.")
        
    deps.global_db = db_service
    
    # 2. Khởi tạo AI Services (Embedding, FAISS, BM25)
    embedder = EmbeddingService()
    faiss_idx = FAISSIndex(dimension=embedder.dimension)
    bm25_idx = BM25Retriever()
    
    index_dir = settings.INDEX_DIR
    
    if (index_dir / "faiss.faiss").exists() and (index_dir / "bm25.pkl").exists():
        logger.info(f"Loading indexes from {index_dir}")
        faiss_idx.load(index_dir / "faiss")
        bm25_idx.load(index_dir / "bm25.pkl")
    else:
        logger.warning(f"Indexes not found in {index_dir}. Search functionality will be empty.")
        
    hybrid_retriever = HybridRetriever(faiss_idx, bm25_idx, embedder)
    deps.global_retriever = hybrid_retriever
    
    # 3. Khởi tạo Pandas Code Executor (đã bọc timeout an toàn)
    deps.global_executor = PandasExecutor()
    
    # 3.5 Khởi tạo Table Loader
    deps.global_table_loader = TableLoader(db_service)
    
    # 4. Khởi tạo LLM Service
    prompt_builder = PromptBuilder()
    context_builder = ContextBuilder()
    deps.global_llm = LLMService(prompt_builder, context_builder)
    
    # 5. Khởi tạo JSON Generator
    deps.global_generator = SubmissionGenerator()
    
    logger.info("✅ All services initialized successfully. Ready to serve requests!")
    yield
    
    # Sự kiện Shutdown: Đóng connection an toàn, tránh memory leak
    logger.info("🛑 Shutting down... Closing Database.")
    db_service.close()

# Cấu hình FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Cấu hình CORS để Frontend (React/NextJS) có thể gọi API mà không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn toàn bộ Routers
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # Chạy Server ở Port 8000
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
