import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api.router import router
import src.api.deps as deps

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Đang khởi động FinAgent API (Phiên bản siêu tốc không chứa Model)...")
    # Warm-up các dependency nhẹ
    deps.get_db_service()
    deps.get_hybrid_retriever()
    deps.get_llm_service()
    logger.info("⚡ API Server đã sẵn sàng trên cổng 8000!")
    yield
    deps.get_db_service().close()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
app.include_router(router, prefix="/api")