import logging
import pandas as pd
import re
from typing import Tuple, Any, Dict
from src.execution.parser_utils import extract_financial_metric

logger = logging.getLogger(__name__)

class PandasExecutor:
    def __init__(self, timeout_sec: int = 15, **kwargs):
        self.timeout_sec = timeout_sec

    def execute(self, code: str, dfs: Dict[str, pd.DataFrame]) -> Tuple[bool, Any]:
        local_vars = {
            'dfs': dfs,
            'pd': pd,
            're': re,
            'extract_financial_metric': extract_financial_metric,
            'result': None
        }
        try:
            exec(code, local_vars, local_vars)
            return True, local_vars.get('result')
        except Exception as e:
            logger.warning(f"Lỗi thực thi Pandas Sandbox: {e}")
            return False, f"ERROR: {str(e)}"
