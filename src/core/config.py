import os
from pathlib import Path
from dotenv import load_dotenv

# Tự động load các biến môi trường từ file .env (nếu có)
load_dotenv()

class Settings:
    """Core application settings and configuration."""
    # App Config
    APP_NAME: str = "NewGenAI Financial Agent"
    APP_VERSION: str = "0.1.0"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "scripts" / "data"
    INDEX_DIR: Path = BASE_DIR / "data" / "index"
    DB_PATH: str = str(BASE_DIR / "data" / "finagent.db")
    
    # Execution
    PANDAS_EXECUTION_TIMEOUT_SEC: int = 5
    
    # Retriever
    TOP_K_RETRIEVAL: int = 5
    
    # LLM (OpenRouter)
    LLM_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    LLM_MODEL: str = "qwen/qwen3-8b"
    LLM_TIMEOUT_SEC: int = int(os.environ.get("LLM_TIMEOUT_SEC", "25"))
    OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
    
    def __init__(self):
        # Ensure directories exist
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
