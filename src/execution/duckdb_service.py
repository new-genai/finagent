import logging
from pathlib import Path
from typing import Optional
import duckdb
import pandas as pd

logger = logging.getLogger(__name__)

class DuckDBService:
    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        self._connect()

    def _connect(self):
        db_file = Path(self.db_path)
        # Đảm bảo thư mục chứa database tồn tại
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Nếu database chưa tồn tại, kết nối ở chế độ ghi để DuckDB tự tạo file mới
        is_read_only = True if db_file.exists() and db_file.stat().st_size > 0 else False
        try:
            self._conn = duckdb.connect(self.db_path, read_only=is_read_only)
            logger.info(f"Connected to DuckDB at {self.db_path} (read_only={is_read_only})")
        except Exception as e:
            logger.error(f"Lỗi kết nối DuckDB: {e}")
            self._conn = None

    def get_connection(self) -> Optional[duckdb.DuckDBPyConnection]:
        if self._conn is None:
            self._connect()
        return self._conn

    def execute_query(self, query: str) -> pd.DataFrame:
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        try:
            return conn.execute(query).df()
        except Exception as e:
            logger.warning(f"Lỗi thực thi truy vấn DuckDB: {e}")
            return pd.DataFrame()

    def get_table_df(self, table_name: str) -> pd.DataFrame:
        query = f'SELECT * FROM "{table_name}"'
        return self.execute_query(query)

    def close(self):
        if self._conn:
            try:
                self._conn.close()
                logger.info("DuckDB connection closed.")
            except Exception as e:
                logger.warning(f"Lỗi đóng kết nối DuckDB: {e}")
            finally:
                self._conn = None