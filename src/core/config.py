import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Core application settings and configuration."""
    APP_NAME: str = "NewGenAI Financial Agent"
    APP_VERSION: str = "0.1.0"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "scripts" / "data"
    INDEX_DIR: Path = BASE_DIR / "data" / "index"
    
    PANDAS_EXECUTION_TIMEOUT_SEC: int = 5
    TOP_K_RETRIEVAL: int = 15
    
    # OpenRouter API với Model ID hợp lệ
    LLM_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    LLM_MODEL: str = "qwen/qwen3-8b"  # Model ID ban đầu hoạt động ổn định
    LLM_TIMEOUT_SEC: int = int(os.environ.get("LLM_TIMEOUT_SEC", "30"))
    LLM_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")

    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()