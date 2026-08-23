import logging
from typing import Dict, List
from pathlib import Path
import pandas as pd
from src.schemas.core import RetrievedTable
from .duckdb_service import DuckDBService
from src.core.config import settings

logger = logging.getLogger(__name__)

class TableLoader:
    def __init__(self, db_service: DuckDBService):
        self.db_service = db_service
        self.csv_dir = settings.BASE_DIR / "data" / "processed" / "csv"

    def load_dataframes(self, tables: List[RetrievedTable]) -> Dict[str, pd.DataFrame]:
        dfs: Dict[str, pd.DataFrame] = {}
        for table in tables:
            t_id = getattr(table, "table_id", None) or str(table)
            duckdb_table = getattr(table, "duckdb_table", None) or t_id
            
            df = pd.DataFrame()
            if self.db_service:
                try:
                    # Bịt miệng log cảnh báo DuckDB cho Terminal sạch đẹp
                    logging.getLogger("src.execution.duckdb_service").setLevel(logging.ERROR)
                    df = self.db_service.get_table_df(duckdb_table)
                except Exception:
                    df = pd.DataFrame()
            
            # Fallback đọc file CSV
            if df is None or df.empty:
                csv_path = self.csv_dir / f"{duckdb_table}.csv"
                if not csv_path.exists():
                    csv_path = self.csv_dir / f"{t_id}.csv"
                if csv_path.exists():
                    try:
                        df = pd.read_csv(csv_path, dtype=str).fillna("")
                        # Xóa sổ cột Unnamed để AI khỏi bị nhầm lẫn
                        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    except Exception:
                        df = pd.DataFrame()
                        
            if df is not None and not df.empty:
                dfs[t_id] = df
                if duckdb_table and duckdb_table != t_id:
                    dfs[duckdb_table] = df
                table.dataframe = df
            else:
                dfs[t_id] = pd.DataFrame()
                
        return dfs
