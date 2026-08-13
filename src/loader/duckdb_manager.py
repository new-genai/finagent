import duckdb
import logging
from pathlib import Path
import pandas as pd
from typing import List, Tuple, Any

# Fix import to use standard python logging instead of custom utils for standalone module
logger = logging.getLogger(__name__)

class DuckDBManager:
    """
    Trình quản lý cơ sở dữ liệu DuckDB.
    Đảm nhiệm việc nạp hàng loạt file CSV vào DuckDB và thực thi truy vấn (Query).
    """
    
    def __init__(self, db_path: str = ":memory:", read_only: bool = False) -> None:
        """
        Khởi tạo kết nối tới DuckDB.
        Mặc định sử dụng ':memory:' (chạy hoàn toàn trên RAM) để tăng tốc độ xử lý
        và tự động xoá sạch dữ liệu sau khi tắt chương trình.
        """
        self.db_path = db_path
        self.conn = duckdb.connect(database=db_path, read_only=read_only)
        logger.info(f"Connected to DuckDB at {db_path} (read_only={read_only})")

    def load(self, csv_dir: Path | str, allowed_tickers: set = None, allowed_years: set = None) -> None:
        """
        Quét toàn bộ thư mục, tìm các file CSV và nạp tự động vào DuckDB.
        Mỗi file CSV sẽ trở thành 1 Table có tên tương ứng với tên file.
        """
        dir_path = Path(csv_dir)
        
        # Validation
        if not dir_path.exists() or not dir_path.is_dir():
            logger.error(f"Invalid directory path: {csv_dir}")
            raise ValueError(f"Invalid directory path: {csv_dir}")
            
        csv_files = list(dir_path.glob("*.csv"))
        if allowed_tickers or allowed_years:
            csv_files = [
                f for f in csv_files 
                if (not allowed_tickers or f.name.split('_')[0].upper() in allowed_tickers)
                and (not allowed_years or f.name.split('_')[1] in allowed_years)
            ]
            
        if not csv_files:
            logger.warning(f"No CSV files found in {csv_dir}")
            return
            
        self.conn.execute("BEGIN TRANSACTION;")
        for idx, file_path in enumerate(csv_files):
            # Lấy tên file làm tên bảng (Table Name). Ví dụ: 'VNM_2023_page1_table1.csv' -> 'VNM_2023_page1_table1'
            table_name = file_path.stem
            
            # Sử dụng cú pháp SQL đặc biệt của DuckDB 'read_csv_auto' 
            # DuckDB sẽ tự động (auto) đọc file, nhận diện Header, và đoán kiểu dữ liệu (Schema Inference)
            query = f"CREATE OR REPLACE TABLE \"{table_name}\" AS SELECT * FROM read_csv_auto('{file_path}');"
            
            try:
                self.conn.execute(query)
                logger.debug(f"Loaded {file_path.name} into table '{table_name}'")
            except Exception as e:
                try:
                    self.conn.execute("ROLLBACK;")
                except Exception:
                    pass
                logger.error(f"Failed to load {file_path.name} into DuckDB: {e}")
                raise
                
            if (idx + 1) % 1000 == 0:
                self.conn.execute("COMMIT;")
                self.conn.execute("BEGIN TRANSACTION;")
                
        try:
            self.conn.execute("COMMIT;")
        except Exception:
            pass

    def query(self, sql_query: str) -> pd.DataFrame:
        """
        Thực thi một câu lệnh SQL SELECT bất kỳ và trả về kết quả dưới dạng Pandas DataFrame.
        """
        logger.debug(f"Executing query: {sql_query}")
        try:
            # df() converts the DuckDB relation to a pandas DataFrame
            result = self.conn.execute(sql_query).df()
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def close(self) -> None:
        """Đóng kết nối cơ sở dữ liệu một cách an toàn."""
        if self.conn:
            self.conn.close()
            logger.info("DuckDB connection closed.")
