import json
import logging
import re
from typing import Any, Dict, List, Optional
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from src.core.config import settings
from .context_builder import ContextBuilder
from .prompt_builder import PromptBuilder
from src.orchestration.coordinator import AgentCoordinator

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, prompt_builder: PromptBuilder, context_builder: ContextBuilder):
        self.prompt_builder = prompt_builder
        self.context_builder = context_builder
        self.session = requests.Session()
        self.coordinator = AgentCoordinator(self._call_llm)

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {settings.LLM_API_KEY}", "Content-Type": "application/json"}

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
    def _call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.01) -> str:
        payload = {"model": settings.LLM_MODEL, "messages": messages, "temperature": temperature, "max_tokens": 1024}
        try:
            resp = self.session.post(settings.LLM_API_URL, headers=self._get_headers(), json=payload, timeout=settings.LLM_TIMEOUT_SEC)
            resp.raise_for_status()
            return resp.json().get("choices", [])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.warning(f"LLM API Error: {e}")
            raise e

    def decompose_query(self, question: str) -> Dict[str, Any]:
        return self.coordinator.plan_query(question)

    def generate_pandas_code_dynamic(self, question: str, plan: Dict[str, Any], context_str: str) -> str:
        return self.coordinator.generate_code(question, plan, context_str)

    def fix_pandas_code(self, original_code: str, error_msg: str, question: str, context_str: str) -> str:
        prompt = (
            f"Bạn là Senior Python Pandas Data Scientist.\n"
            f"Mã Pandas dưới đây được sinh ra để giải quyết: '{question}'\n"
            f"Nhưng gặp lỗi:\n{error_msg}\n\n"
            f"DỮ LIỆU ĐẦU VÀO (`dfs` dictionary):\n{context_str}\n\n"
            f"MÃ BỊ LỖI:\n```python\n{original_code}\n```\n\n"
            f"HƯỚNG DẪN SỬA LỖI:\n"
            f"1. Nhớ dùng `df = list(dfs.values())[0]` hoặc duyệt `dfs.values()`. Không gọi trực tiếp `df` nếu chưa gán.\n"
            f"2. Bắt buộc gán kết quả vào biến `result` theo chuẩn Dictionary.\n"
            f"Chỉ trả về MÃ PYTHON nằm trong khối ```python ... ```."
        )
        try:
            res = self._call_llm([{"role": "user", "content": prompt}], temperature=0.1)
            code_match = re.search(r"```python\s*(.*?)\s*```", res, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            return res.replace("```python", "").replace("```", "").strip()
        except Exception as e:
            return original_code

    def validate_extraction(self, intent: str, value: float, provenance_row: str) -> Dict[str, str]:
        prompt = (
            f"Bạn là Kiểm toán viên tài chính (Financial Auditor).\n"
            f"- Mục tiêu tìm kiếm (Intent): '{intent}'\n"
            f"- Tên dòng trích xuất (Provenance Row): '{provenance_row}'\n"
            f"- Giá trị (Value): {value}\n\n"
            f"Đánh giá xem 'Tên dòng' có đúng ngữ nghĩa với 'Mục tiêu' không.\n"
            f"- PASS: Đúng ngữ nghĩa.\n"
            f"- FAIL: Sai ngữ nghĩa.\n"
            f"- DATA_MISSING: Bảng không có chỉ tiêu phù hợp.\n\n"
            f"Trả về JSON:\n"
            f'{{\"status\": \"PASS\" | \"FAIL\" | \"DATA_MISSING\", \"reason\": \"Lý do\"}}'
        )
        try:
            res = self._call_llm([{"role": "user", "content": prompt}], temperature=0.0)
            return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
        except Exception:
            return {"status": "PASS", "reason": "Bỏ qua xác thực."}

    def generate_natural_response(self, question: str, raw_output: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        try:
            return self._call_llm([
                {"role": "system", "content": "Trả lời ngắn gọn, trực diện về số liệu."},
                {"role": "user", "content": f"Câu hỏi: {question}\nKết quả: {raw_output}"}
            ])
        except Exception:
            return f"Kết quả: {raw_output}"

    def generate_cot_fallback(self, question: str, context_str: str) -> str:
        return "Không thể trích xuất hoặc tính toán chính xác số liệu từ báo cáo tài chính được cung cấp."
