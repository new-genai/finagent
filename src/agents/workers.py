import re
import logging

logger = logging.getLogger(__name__)

class DynamicPandasWorker:
    def __init__(self, llm_call):
        self.llm_call = llm_call

    def generate_code(self, question: str, plan, context_str: str) -> str:
        if isinstance(plan, dict):
            year_target = str(plan.get("year")) if plan.get("year") else "2023"
        else:
            year_target = str(plan.year) if plan and getattr(plan, "year", None) else "2023"
            
        prompt = (
            "Bạn là một chuyên gia Data. Nhiệm vụ của bạn là lấy số liệu tài chính.\n"
            f"Câu hỏi: '{question}'\n"
            f"Năm: '{year_target}'\n\n"
            "THÔNG TIN CÁC BẢNG DỮ LIỆU ĐANG CÓ (Bạn PHẢI dựa vào thông tin này để chọn keywords chính xác có trong bảng):\n"
            f"{context_str}\n\n"
            "BẠN ĐƯỢC CUNG CẤP HÀM SAU:\n"
            "`extract_financial_metric(dfs, keywords: List[str], year: str, get_max: bool = True) -> float`\n\n"
            "MẪU CODE BẮT BUỘC:\n"
            "```python\n"
            "# Thay đổi keywords theo chỉ tiêu cần tìm. RẤT QUAN TRỌNG:\n"
            "# - Doanh thu -> ['doanh thu bán hàng', 'doanh thu thuần']\n"
            "# - Lợi nhuận -> ['lợi nhuận sau thuế của cổ đông công ty mẹ', 'lợi nhuận sau thuế thu nhập doanh nghiệp']\n"
            "# - Tài sản -> ['tổng cộng tài sản']\n"
            "# - Nhóm 5 -> ['nhóm 5', 'nợ có khả năng mất vốn']\n"
            "keywords = ['từ khóa 1', 'từ khóa 2']\n"
            f"val = extract_financial_metric(dfs, keywords, '{year_target}', get_max=True)\n"
            "if val is not None:\n"
            "    result = {\"value\": val, \"provenance\": {\"table_id\": \"auto\", \"row_name\": \"auto\", \"column_name\": \"auto\"}}\n"
            "else:\n"
            "    result = None\n"
            "```\n\n"
            "Hãy trả về mã Python trong khối ```python ... ```."
        )
        
        try:
            res = self.llm_call([
                {"role": "system", "content": "You are a senior Python Pandas data extraction expert."},
                {"role": "user", "content": prompt}
            ], temperature=0.1)
            code_match = re.search(r"```python\s*(.*?)\s*```", res, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            return res.replace("```python", "").replace("```", "").strip()
        except Exception as e:
            logger.error(f"Lỗi DynamicPandasWorker: {e}")
            return "result = None"
