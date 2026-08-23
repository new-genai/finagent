import pandas as pd
from typing import List, Dict
import logging
from src.schemas.core import RetrievedTable
from src.core.db import DuckDBService

logger = logging.getLogger(__name__)

class TableLoader:
    def __init__(self, db_service: DuckDBService):
        self.db_service = db_service

    def load_dataframes(self, tables: List[RetrievedTable]) -> Dict[str, pd.DataFrame]:
        dfs = {}
        con = self.db_service.get_connection()
        for t in tables:
            if not t.duckdb_table:
                continue
            try:
                df = con.execute(f'SELECT * FROM "{t.duckdb_table}"').df()
                
                if not df.empty:
                    # Chuẩn hóa tên cột đầu tiên thành 'Chi_tieu'
                    first_col = df.columns[0]
                    df.rename(columns={first_col: 'Chi_tieu'}, inplace=True)
                    
                    # Nếu cột đầu tiên bị NaN, điền bằng tên gốc của cột
                    if df['Chi_tieu'].isna().sum() > len(df) * 0.3:
                        fill_val = str(first_col) if "Unnamed" not in str(first_col) else "Chi tieu"
                        df['Chi_tieu'] = df['Chi_tieu'].fillna(fill_val)
                    else:
                        df['Chi_tieu'] = df['Chi_tieu'].astype(str)

                dfs[t.table_id] = df
            except Exception as e:
                logger.error(f"Lỗi nạp bảng {t.table_id}: {e}")
                
        return dfs