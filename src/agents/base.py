from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any

class TaskType(str, Enum):
    FINANCIAL_METRIC = "FINANCIAL_METRIC"
    LOAN_CLASSIFICATION = "LOAN_CLASSIFICATION"
    AGGREGATION_MATH = "AGGREGATION_MATH"
    COMPLEX_DERIVED = "COMPLEX_DERIVED"
    SIMPLE_DERIVED = "SIMPLE_DERIVED"

class ExecutionStep(BaseModel):
    step_id: str
    metric_intent: str
    sub_queries: List[str] = []

class QueryPlan(BaseModel):
    task_type: TaskType = TaskType.FINANCIAL_METRIC
    companies: List[str] = []
    years: List[str] = []
    sub_queries: List[str] = []
    operation: str = "NONE"
    is_complex: bool = False
    steps: List[ExecutionStep] = []
    final_formula: Optional[str] = ""
