import logging
from typing import List, Dict
import pandas as pd

from src.schemas.core import RetrievedTable
from src.database.duckdb_service import DuckDBService

logger = logging.getLogger(__name__)

class TableLoader:
    """Service to load actual DataFrames from DuckDB for retrieved tables."""
    
    def __init__(self, db_service: DuckDBService):
        self.db = db_service
        
    def load_dataframes(self, tables: List[RetrievedTable]) -> Dict[str, pd.DataFrame]:
        """
        Queries DuckDB to get the DataFrame for each table in the list.
        Populates the .dataframe attribute of each RetrievedTable.
        Returns a dictionary mapping table_name to pd.DataFrame.
        """
        dfs = {}
        for table in tables:
            table_name = table.duckdb_table if table.duckdb_table else table.table_id
            try:
                # Need to wrap table_name in quotes in case it has special characters or spaces
                query = f'SELECT * FROM "{table_name}"'
                df = self.db.query(query)
                if df is not None:
                    table.dataframe = df
                    dfs[table.table_id] = df
                    logger.info(f"Loaded DataFrame for {table_name}, shape: {df.shape}")
            except Exception as e:
                logger.error(f"Failed to load DataFrame for table '{table_name}': {e}")
                
        return dfs
