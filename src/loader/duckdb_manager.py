import duckdb
import logging
from pathlib import Path
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

class DuckDBManager:
    """Trình quản trị DuckDB, nạp CSV vào Database an toàn."""
    def __init__(self, db_path: str = ":memory:", read_only: bool = False) -> None:
        self.db_path = db_path
        self.conn = duckdb.connect(database=db_path, read_only=read_only)
        if not read_only:
            self.conn.execute("PRAGMA memory_limit='4GB';")
            self.conn.execute("PRAGMA threads=2;")
        logger.info(f"Connected to DuckDB at {db_path} (read_only={read_only})")

    def load(self, csv_dir: Path | str, allowed_tickers: Optional[set] = None, allowed_years: Optional[set] = None) -> None:
        dir_path = Path(csv_dir)
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid directory path: {csv_dir}")
            
        csv_files = list(dir_path.glob("*.csv"))
        if allowed_tickers or allowed_years:
            csv_files = [
                f for f in csv_files
                if (not allowed_tickers or f.name.split('_')[0].upper() in allowed_tickers)
                and (not allowed_years or f.name.split('_')[1] in allowed_years)
            ]
            
        if not csv_files:
            return
        
        self.conn.execute("BEGIN TRANSACTION;")
        loaded_count = 0
        for idx, file_path in enumerate(csv_files):
            if file_path.stat().st_size == 0:
                continue
            
            table_name = file_path.stem
            posix_path = file_path.as_posix().replace("'", "''")
            
            # Khóa chặt định dạng VARCHAR cho mọi cột
            query = f"""
                CREATE OR REPLACE TABLE "{table_name}" AS 
                SELECT * FROM read_csv('{posix_path}', 
                    auto_detect=true, 
                    all_varchar=true,
                    ignore_errors=true, 
                    null_padding=true,
                    header=true
                );
            """
            try:
                self.conn.execute(query)
                loaded_count += 1
            except Exception as e:
                logger.debug(f"Bỏ qua bảng lỗi {file_path.name}: {e}")
                
            if (idx + 1) % 500 == 0:
                self.conn.execute("COMMIT;")
                self.conn.execute("PRAGMA force_checkpoint;")
                self.conn.execute("BEGIN TRANSACTION;")
                logger.info(f"Nạp {loaded_count}/{len(csv_files)} bảng vào DuckDB...")
                
        try:
            self.conn.execute("COMMIT;")
            self.conn.execute("PRAGMA force_checkpoint;")
            logger.info(f"Hoàn tất nạp {loaded_count} bảng vào DuckDB.")
        except Exception:
            pass

    def query(self, sql_query: str) -> pd.DataFrame:
        try:
            return self.conn.execute(sql_query).df()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            logger.info("DuckDB connection closed.")