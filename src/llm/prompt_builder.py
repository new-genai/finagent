class PromptBuilder:
    """Xây dựng Prompt cho LLM dựa trên Context Builder."""
    
    def build_prompt(self, question: str, context_str: str) -> str:
        """
        Tạo prompt yêu cầu LLM viết code Pandas dựa trên các DataFrame đã được load.
        """
        prompt = f"""Bạn là một chuyên gia phân tích dữ liệu tài chính (Data Analyst).
Nhiệm vụ của bạn là viết code Python (sử dụng thư viện Pandas) để phân tích các DataFrame và trả lời câu hỏi của người dùng.

{context_str}

CÂU HỎI CỦA NGƯỜI DÙNG:
{question}

LUẬT THỰC THI (QUAN TRỌNG):
1. Bạn KHÔNG được bịa dữ liệu. Bạn CHỈ ĐƯỢC sử dụng các DataFrame đã cung cấp trong biến `dfs` (ví dụ: `df = dfs['VNM_2023_page1_table1']`).
2. KHÔNG tạo thêm bất kỳ DataFrame giả nào. Nếu dữ liệu cung cấp không đủ để trả lời câu hỏi, hãy gán `result = "Không tìm thấy thông tin."`
3. KHÔNG sử dụng cơ sở dữ liệu SQL (Không dùng `db.query`). Chỉ sử dụng Pandas thao tác trên các biến có sẵn.
4. KHÔNG import thêm bất kỳ thư viện nào khác ngoài pandas (đã có sẵn `pd`).
5. Kết quả cuối cùng BẮT BUỘC phải được gán vào biến tên là `result`.
6. Nếu câu trả lời là một con số, hãy sử dụng f-string để định dạng thành câu tiếng Việt hoàn chỉnh (VD: `result = f"Doanh thu của VNM năm 2023 là {{val}} tỷ đồng."`). Nếu kết quả là DataFrame, cứ gán thẳng `result = df`.
7. CHỈ TRẢ VỀ DUY NHẤT CODE PYTHON. Không giải thích, không output thêm bất kỳ văn bản nào ngoài block code.
"""
        return prompt
