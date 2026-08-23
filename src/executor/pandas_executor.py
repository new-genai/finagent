import logging
import pandas as pd
from typing import Tuple
from src.core.config import settings
from src.database.duckdb_service import DuckDBService

# Import class làm sạch dữ liệu tài chính
from src.metadata.normalizer import FinancialDataCleaner

logger = logging.getLogger(__name__)

class PandasExecutor:
    """Thực thi mã Pandas sinh bởi LLM trong môi trường Sandbox."""
    
    def __init__(self):
        self.timeout = settings.PANDAS_EXECUTION_TIMEOUT_SEC

    def _is_safe(self, code: str) -> bool:
        """Kiểm tra mã độc (os, sys, subprocess...)."""
        banned = ["os", "sys", "subprocess", "eval", "exec", "open", "__import__"]
        for b in banned:
            if b in code:
                return False
        return True

    def execute(self, code: str, dfs: dict) -> Tuple[bool, str]:
        """Thực thi mã Pandas an toàn."""
        logger.info("Executing LLM Generated Pandas code...")
        
        if not self._is_safe(code):
            return False, "Code execution blocked due to security reasons."
            
        # Nạp pandas, dict các dataframes và ĐẶC BIỆT là hàm parse số liệu vào Sandbox
        local_vars = {
            "pd": pd, 
            "dfs": dfs,
            "parse_vn_financial_number": FinancialDataCleaner.parse_vn_financial_number
        }
        
        wrapped_code = f"""
try:
{chr(10).join(['    ' + line for line in code.split(chr(10))])}
except Exception as e:
    result = f'ERROR: {{str(e)}}'
"""
        try:
            exec(wrapped_code, {}, local_vars)
            output = local_vars.get("result", "No 'result' variable found in code.")
            if isinstance(output, str) and output.startswith("ERROR:"):
                return False, output
            return True, str(output)
        except Exception as e:
            return False, str(e)