from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RetrieveRequest(BaseModel):
    """Request model for retrieving tables based on a question."""
    question: str = Field(..., description="The user's question to retrieve context for.")

class RetrievedTable(BaseModel):
    """Model representing a retrieved table."""
    table_id: str
    company: str
    year: str
    score: float
    preview: Optional[List[List[str]]] = None

class RetrieveResponse(BaseModel):
    """Response model for retrieval."""
    tables: List[RetrievedTable]

class ExecuteRequest(BaseModel):
    """Request model for executing Pandas code."""
    code: str = Field(..., description="The pandas code to execute.")

class ExecuteResponse(BaseModel):
    """Response model for code execution."""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None

class ChatRequest(BaseModel):
    """Request model for the main chat endpoint."""
    question: str = Field(..., description="The user's question.")
    history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Previous messages in the chat.")

class ChatResponse(BaseModel):
    """Response model for the main chat endpoint."""
    answer: str
    thought_process: Optional[str] = None
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
