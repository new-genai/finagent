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
    tables_used: List[str] = []
    
class SubmissionRequest(BaseModel):
    """Request to generate the final submission JSON."""
    pass

class DatasetStatsResponse(BaseModel):
    """Response model for dataset statistics."""
    total_files: int
    total_tables: int
    companies: List[str]
    years: List[str]
    company_table_counts: Dict[str, int] = {}
    year_table_counts: Dict[str, int] = {}

class RetrieveRequest(BaseModel):
    question: str

class RetrieveResponse(BaseModel):
    tables: List[Any]

class ExecuteRequest(BaseModel):
    code: str

class ExecuteResponse(BaseModel):
    success: bool
    result: Any = None
    error: Any = None
