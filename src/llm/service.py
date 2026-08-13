import logging
import requests
import json
from typing import List, Dict, Any, Optional

from .prompt_builder import PromptBuilder
from .context_builder import ContextBuilder
from src.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """
    Giao tiếp với mô hình ngôn ngữ lớn (LLM).
    Bản MVP này đang tạm thời Mock (giả lập) LLM trả về code mẫu.
    Kiến trúc này cho phép sau này dễ dàng đổi ruột gọi OpenAI hoặc Ollama API.
    """
    def __init__(self, prompt_builder: PromptBuilder, context_builder: ContextBuilder):
        self.prompt_builder = prompt_builder
        self.context_builder = context_builder
        self.session = requests.Session()
        
    def generate_pandas_code(self, question: str, context_str: str) -> str:
        """Tạo code Pandas dựa trên câu hỏi và ngữ cảnh các bảng."""
        prompt = self.prompt_builder.build_prompt(question, context_str)
        logger.debug(f"Generated Prompt: \n{prompt}")
        
        if not context_str or "Không có dữ liệu" in context_str:
            return "result = 'Không tìm thấy dữ liệu bảng phù hợp để trả lời câu hỏi này.'"
            
        try:
            logger.info(f"Calling OpenRouter API ({settings.LLM_MODEL})...")
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            response = self.session.post(
                settings.LLM_API_URL,
                headers=headers,
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a senior Data Analyst. Generate pandas code only. Use the provided context to answer user queries accurately. Return raw python code."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.0
                },
                timeout=settings.LLM_TIMEOUT_SEC
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract content from OpenRouter / OpenAI response format
            choices = data.get("choices", [])
            if choices and isinstance(choices, list):
                generated_code = choices[0].get("message", {}).get("content", "")
            else:
                generated_code = ""
                
            # Clean up markdown if any
            if "```python" in generated_code:
                code = generated_code.split("```python")[1].split("```")[0]
            elif "```" in generated_code:
                code = generated_code.split("```")[1].split("```")[0]
            else:
                code = generated_code
            
            clean_code = code.strip()
            logger.info(f"Generated Code: \n{clean_code}")
                
            return clean_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to OpenRouter: {e}")
            return f"result = 'Lỗi kết nối LLM (OpenRouter): {str(e)}'"
        except Exception as e:
            logger.error(f"Unexpected error in LLM service: {e}")
            return f"result = 'Lỗi không xác định khi gọi LLM: {str(e)}'"

    def generate_natural_response(self, question: str, raw_output: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        """Tạo câu trả lời tự nhiên từ kết quả thô của đoạn code."""
        try:
            logger.info(f"Calling OpenRouter API for Natural Response ({settings.LLM_MODEL})...")
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            system_prompt = (
                "Bạn là một trợ lý ảo tài chính thông minh, nhiệt tình và chuyên nghiệp tên là AI Guru (hoạt động giống như ChatGPT). "
                "Nhiệm vụ của bạn là nhận kết quả thô (raw output) từ câu truy vấn dữ liệu và trả lời người dùng một cách tự nhiên bằng tiếng Việt. "
                "YÊU CẦU QUAN TRỌNG: "
                "1. Luôn xưng 'tôi' và gọi người dùng là 'bạn'. "
                "2. Câu trả lời phải có đầy đủ chủ ngữ, vị ngữ, diễn đạt trôi chảy, mạch lạc, có đầu có đuôi như một con người đang trò chuyện. KHÔNG trả lời cộc lốc, máy móc hay công nghiệp. "
                "3. Trả lời chi tiết, đầy đủ ý, giải thích rõ kết quả lấy từ đâu nhưng không lan man lòng vòng. "
                "4. Dựa vào lịch sử chat (nếu có) để duy trì mạch trò chuyện liền mạch. "
                "5. Nếu kết quả thô là DataFrame/bảng biểu, hãy trình bày lại rõ ràng, đẹp mắt bằng bảng markdown. "
                "6. Nếu kết quả là lỗi hoặc không tìm thấy, hãy xin lỗi nhẹ nhàng và đề xuất hướng giải quyết."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            if history:
                for msg in history[-5:]: # Chỉ lấy 5 tin nhắn gần nhất để tránh quá tải context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role in ("user", "assistant"):
                        messages.append({"role": role, "content": content})
                        
            user_prompt = f"Câu hỏi của người dùng: {question}\nKết quả trích xuất được: {raw_output}\nHãy viết lại câu trả lời thật tự nhiên:"
            messages.append({"role": "user", "content": user_prompt})
            
            response = self.session.post(
                settings.LLM_API_URL,
                headers=headers,
                json={
                    "model": "google/gemini-2.5-flash:free",
                    "messages": messages,
                    "temperature": 0.3
                },
                timeout=settings.LLM_TIMEOUT_SEC
            )
            response.raise_for_status()
            
            data = response.json()
            choices = data.get("choices", [])
            if choices and isinstance(choices, list):
                return choices[0].get("message", {}).get("content", "").strip()
            return raw_output
        except Exception as e:
            logger.error(f"Error generating natural response: {e}")
            return str(raw_output)

    def analyze_intent_and_extract(self, question: str, history: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Sử dụng LLM để phân loại intent và trích xuất các entities (tickers, years, metrics).
        Đồng thời rewrite lại câu hỏi nếu là financial_query, hoặc sinh câu trả lời trực tiếp nếu là conversation.
        """
        try:
            logger.info("Analyzing intent and extracting entities...")
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            
            history_str = ""
            if history:
                for msg in history[-5:]: # Limit context
                    role = "Người dùng" if msg.get("role") == "user" else "Trợ lý"
                    content = msg.get("content", "")
                    history_str += f"{role}: {content}\n"
                    
            system_prompt = (
                "Bạn là một AI Router và Entity Extractor cho hệ thống AI Financial Data Assistant. "
                "Hệ thống chỉ hỗ trợ truy vấn báo cáo tài chính của các công ty chứng khoán Việt Nam (VNM, FPT, VIC, HPG, MWG, VCB, v.v.). "
                "Nhiệm vụ của bạn là đọc lịch sử hội thoại (nếu có) và câu hỏi cuối cùng của người dùng, sau đó trả về ĐÚNG định dạng JSON sau:\n"
                "{\n"
                '  "intent": "financial_query" | "conversation" | "clarification" | "unsupported",\n'
                '  "rewritten_query": "câu hỏi hoàn chỉnh đầy đủ ngữ cảnh (chỉ dùng nếu financial_query)",\n'
                '  "tickers": ["VNM", "FPT"],\n'
                '  "years": ["2022", "2023"],\n'
                '  "direct_answer": "Câu trả lời trực tiếp phản hồi lại user một cách tự nhiên (nếu intent KHÔNG PHẢI financial_query)"\n'
                "}\n\n"
                "Giải thích Intent:\n"
                "- financial_query: Câu hỏi yêu cầu lấy số liệu, tính toán, biểu đồ về báo cáo tài chính. (Ví dụ: 'doanh thu vnm 2022', 'vnm 2022', 'lợi nhuận là bao nhiêu?'). "
                "LƯU Ý: Nếu user chỉ nói 'không, lợi nhuận' sau khi hỏi doanh thu, đây CŨNG LÀ financial_query.\n"
                "- conversation: Chào hỏi, cảm ơn, đính chính, hội thoại ngoài luồng. (Ví dụ: 'có hỏi doanh thu đâu', 'xin chào', 'đúng rồi', 'sai rồi').\n"
                "- clarification: Câu hỏi chưa đủ context để tra cứu (Ví dụ: chỉ nói 'VNM', hoặc 'doanh thu' mà chưa biết mã nào/năm nào).\n"
                "- unsupported: Câu hỏi không liên quan tài chính.\n\n"
                "Quy tắc Entity Extraction (RẤT QUAN TRỌNG):\n"
                "1. tickers: CHỈ chứa các mã chứng khoán viết hoa (VD: 'VNM', 'FPT', 'HPG'). Nếu user nhập 'vnm', 'doanh thu vnm' -> mảng phải có 'VNM'. "
                "KHÔNG đưa các từ như 'CÔNG', 'TY', 'MÃ' vào tickers.\n"
                "2. years: Lọc các năm (VD: '2022', '2023').\n"
                "3. rewritten_query: Phải chứa ĐẦY ĐỦ tickers, năm, chỉ tiêu dựa vào cả câu hỏi hiện tại và lịch sử. Không dùng đại từ thay thế.\n\n"
                "BẮT BUỘC TRẢ VỀ CHUẨN JSON, KHÔNG CÓ BẤT KỲ VĂN BẢN NÀO KHÁC BÊN NGOÀI."
            )
            
            user_prompt = f"Lịch sử trò chuyện:\n{history_str}\nCâu hỏi hiện tại: {question}"
            
            response = self.session.post(
                settings.LLM_API_URL,
                headers=headers,
                json={
                    "model": "google/gemini-2.5-flash:free",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.0
                },
                timeout=settings.LLM_TIMEOUT_SEC
            )
            response.raise_for_status()
            
            data = response.json()
            choices = data.get("choices", [])
            if choices and isinstance(choices, list):
                content = choices[0].get("message", {}).get("content", "").strip()
                # Clean up markdown if any
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                elif content.startswith("```"):
                    content = content[3:-3].strip()
                
                try:
                    parsed = json.loads(content)
                    logger.info(f"LLM Extracted Intent: {parsed}")
                    
                    # Chuẩn hóa tickers
                    if "tickers" in parsed and isinstance(parsed["tickers"], list):
                        parsed["tickers"] = [t.upper().strip() for t in parsed["tickers"] if isinstance(t, str)]
                        
                    return parsed
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from LLM: {content}. Error: {e}")
                    
            # Fallback
            return {
                "intent": "financial_query",
                "rewritten_query": question,
                "tickers": [],
                "years": [],
                "direct_answer": ""
            }
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {
                "intent": "financial_query",
                "rewritten_query": question,
                "tickers": [],
                "years": [],
                "direct_answer": ""
            }
