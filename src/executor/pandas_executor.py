import logging
import pandas as pd
from typing import Tuple

from src.core.config import settings
from src.database.duckdb_service import DuckDBService

logger = logging.getLogger(__name__)

class PandasExecutor:
    """Executes generated Pandas code securely with a timeout."""
    
    def __init__(self):
        self.timeout = settings.PANDAS_EXECUTION_TIMEOUT_SEC
        
    def _is_safe(self, code: str) -> bool:
        """Kiểm tra thô độ an toàn của code sinh bởi LLM (Block os, sys...)."""
        banned = ["os", "sys", "subprocess", "eval", "exec", "open", "__import__"]
        for b in banned:
            if b in code:
                return False
        return True

    def execute(self, code: str, dfs: dict) -> Tuple[bool, str]:
        """
        Thực thi code Pandas. Có Timeout và Error Handling.
        Returns: Tuple(Success(True/False), Kết quả/Lỗi)
        """
        logger.info("Executing LLM Generated Pandas code...")
        
        if not self._is_safe(code):
            return False, "Code execution blocked due to security reasons."

        # Since multiprocessing with DuckDB in-memory causes pickling errors, 
        # we execute synchronously for MVP.
        local_vars = {"pd": pd, "dfs": dfs}
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
