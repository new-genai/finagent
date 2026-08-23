from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional

class RetrievedTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    table_id: str
    duckdb_table: str = ""
    company: str
    year: str
    score: float = 0.0
    columns: List[str] = Field(default_factory=list)
    dataframe: Any = None

class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question.")
    history: Optional[List[Dict[str, Any]]] = Field(default=None)

class Evidence(BaseModel):
    variable: str
    csv_path: str

class ChatResponse(BaseModel):
    answer: str
    thought_process: Optional[str] = None
    relevant_docs: List[str] = []
    relevant_tables: List[str] = []
    evidence: List[Evidence] = []
    pandas_query: str = ""
