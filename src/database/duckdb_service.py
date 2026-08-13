import logging
from typing import List, Tuple, Any
from pathlib import Path

from src.loader.duckdb_manager import DuckDBManager
from src.core.config import settings

logger = logging.getLogger(__name__)

class DuckDBService:
    """Service layer for DuckDB database operations."""
    
    def __init__(self, db_path: str | None = None, read_only: bool = False):
        self.manager = DuckDBManager(db_path or settings.DB_PATH, read_only=read_only)
        self._is_loaded = False
        
    def load(self, csv_dir: Path | str) -> None:
        """Nạp dữ liệu từ thư mục CSV nếu chưa nạp."""
        if not self._is_loaded:
            logger.info(f"Loading CSV data from {csv_dir} into DuckDB...")
            self.manager.load(csv_dir)
            self._is_loaded = True
            
    def query(self, sql_query: str) -> List[Tuple[Any, ...]]:
        """Thực thi câu truy vấn SQL."""
        return self.manager.query(sql_query)
        
    def close(self) -> None:
        """Đóng kết nối cơ sở dữ liệu."""
        self.manager.close()
