import logging
from typing import Dict, List
from pathlib import Path
import pandas as pd
from src.schemas.core import RetrievedTable
from src.core.config import settings

logger = logging.getLogger(__name__)

class TableLoader:
    def __init__(self):
        self.csv_dir = settings.BASE_DIR / "data" / "processed" / "csv"

    def load_dataframes(self, tables: List[RetrievedTable]) -> Dict[str, pd.DataFrame]:
        dfs: Dict[str, pd.DataFrame] = {}
        for table in tables:
            t_id = getattr(table, "table_id", None) or str(table)
            duckdb_table = getattr(table, "duckdb_table", None) or t_id
            
            df = pd.DataFrame()
            csv_path = self.csv_dir / f"{duckdb_table}.csv"
            if not csv_path.exists():
                csv_path = self.csv_dir / f"{t_id}.csv"
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path, dtype=str).fillna("")
                    # Xóa sổ cột Unnamed để AI khỏi bị nhầm lẫn, nhưng giữ lại Unnamed: 0 là cột Chỉ tiêu
                    if 'Unnamed: 0' in df.columns:
                        df = df.rename(columns={'Unnamed: 0': 'Chỉ tiêu'})
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
