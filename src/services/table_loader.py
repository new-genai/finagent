import logging
import pandas as pd
from typing import List, Dict
from src.schemas.core import RetrievedTable
from src.metadata.normalizer import FinancialDataCleaner
from src.core.config import settings

logger = logging.getLogger(__name__)

class TableLoader:
    def __init__(self, db_service=None):
        self.csv_dir = settings.BASE_DIR / "data" / "processed" / "csv"

    def _safe_parse_number(self, val):
        if pd.isna(val) or val is None or str(val).strip() == "":
            return val
        parsed_val = FinancialDataCleaner.parse_vn_financial_number(val)
        return val if pd.isna(parsed_val) else parsed_val

    def load_dataframes(self, tables: List[RetrievedTable]) -> Dict[str, pd.DataFrame]:
        dfs: Dict[str, pd.DataFrame] = {}
        seen_ids = set()
        
        for table in tables:
            if table.table_id in seen_ids:
                continue
            seen_ids.add(table.table_id)
            
            table_name = table.duckdb_table if table.duckdb_table else table.table_id
            csv_path = self.csv_dir / f"{table_name}.csv"
            
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path)
                    df = df.dropna(how="all", axis=1)
                    
                    if "ROW_ID" not in df.columns:
                        df.insert(0, "ROW_ID", [f"ROW_{idx}" for idx in range(len(df))])
                        
                    for col in df.columns:
                        if col == "ROW_ID":
                            continue
                        df[col] = df[col].apply(self._safe_parse_number)
                        
                    table.dataframe = df
                    dfs[table.table_id] = df
                except Exception as e:
                    logger.debug(f"Bỏ qua bảng lỗi {table_name}: {e}")
                    
        return dfs