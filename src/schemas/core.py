from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any

class RetrievedTable(BaseModel):
    """Core model representing a retrieved table with its dataframe and metadata."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    table_id: str
    duckdb_table: str = ""
    company: str
    year: str
    score: float = 0.0
    columns: List[str] = Field(default_factory=list)
    dataframe: Any = None  # Holds pd.DataFrame
