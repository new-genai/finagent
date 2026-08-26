import logging
import json
import re
from src.agents.base import QueryPlan, TaskType, ExecutionStep

logger = logging.getLogger(__name__)

class RouterAgent:
    def __init__(self, llm_call):
        self.llm_call = llm_call

    def analyze(self, question: str) -> QueryPlan:
        q_lower = question.lower()
        
        prompt = (
            "Bạn là một chuyên gia phân tích yêu cầu tài chính.\n"
            f"Câu hỏi: '{question}'\n\n"
            "Hãy trích xuất danh sách các công ty (Mã chứng khoán 3 chữ cái HOẶC tên viết tắt) và các năm được nhắc đến trong câu hỏi.\n"
            "LƯU Ý QUAN TRỌNG: Nếu câu hỏi nhắc đến TÊN công ty mà không có mã, hãy quy đổi sang mã 3 chữ cái nếu bạn biết (VD: Vinamilk -> VNM, Đô thị Kinh Bắc -> KBC, Đức Long Gia Lai -> DLG). Nếu câu hỏi liệt kê một nhóm (VD: VIC-NVL-VRE-KBC-SCR-VPI), hãy liệt kê ĐẦY ĐỦ các mã đó.\n"
            "Trả về kết quả dưới định dạng JSON CHÍNH XÁC (không có markdown):\n"
            '{"companies": ["VNM", "KBC"], "years": ["2023", "2024"]}\n'
            "Nếu không có công ty nào, trả về mảng rỗng []."
        )
        
        companies = []
        years = []
        try:
            res = self.llm_call([{"role": "user", "content": prompt}], temperature=0.0)
            json_str = re.search(r"\{.*\}", res, re.DOTALL)
            if json_str:
                data = json.loads(json_str.group(0))
                companies = [str(c).upper() for c in data.get("companies", [])]
                years = [str(y) for y in data.get("years", [])]
        except Exception as e:
            logger.error(f"RouterAgent LLM extraction failed: {e}")
            # Fallback to simple regex if LLM fails
            company_matches = re.findall(r'\b[A-Z]{3}\b', question)
            companies = list(set(company_matches))
            year_matches = re.findall(r'\b(201[0-9]|202[0-9])\b', question)
            years = list(set(year_matches))

        sq_list = []
        if "doanh thu" in q_lower and "lợi nhuận" in q_lower:
            sq_list = [
                ["doanh thu bán hàng và cung cấp dịch vụ", "kết quả kinh doanh", "hợp nhất"],
                ["lợi nhuận sau thuế của cổ đông công ty mẹ", "lợi nhuận sau thuế thu nhập doanh nghiệp", "kết quả kinh doanh", "hợp nhất"]
            ]
        elif "doanh thu" in q_lower:
            sq_list = [["doanh thu bán hàng và cung cấp dịch vụ", "kết quả kinh doanh", "hợp nhất"]]
        elif "lợi nhuận" in q_lower or "lnst" in q_lower:
            sq_list = [["lợi nhuận sau thuế của cổ đông công ty mẹ", "lợi nhuận sau thuế thu nhập doanh nghiệp", "kết quả kinh doanh", "hợp nhất"]]
        elif "nhóm 5" in q_lower or "nợ xấu" in q_lower:
            sq_list = [["nợ có khả năng mất vốn", "nhóm 5", "cho vay khách hàng", "hợp nhất"]]
        elif "tài sản" in q_lower:
            sq_list = [["tổng cộng tài sản", "bảng cân đối kế toán", "hợp nhất"]]
        else:
            sq_list = [[question, "hợp nhất"]]

        steps = []
        for idx, sq in enumerate(sq_list, 1):
            intent = "Doanh thu" if "doanh thu" in sq[0] else ("Lợi nhuận" if "lợi nhuận" in sq[0] else sq[0])
            steps.append(ExecutionStep(step_id=f"step_{idx}", metric_intent=intent, sub_queries=sq))

        plan = QueryPlan(
            task_type=TaskType.COMPLEX_DERIVED if len(steps) > 1 else TaskType.FINANCIAL_METRIC,
            companies=companies,
            years=years,
            sub_queries=sq_list[0],
            operation="SUM" if len(steps) > 1 else "NONE",
            is_complex=len(steps) > 1,
            steps=steps,
            final_formula="step_1 + step_2" if len(steps) > 1 else "step_1"
        )
        return plan
