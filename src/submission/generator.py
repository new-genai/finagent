import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SubmissionGenerator:
    """Sinh file JSON nộp bài cuối cùng (Submission) cho ban giám khảo."""
    
    def generate(self, answers: Dict[str, Any], output_path: Path | str) -> None:
        """
        Đóng gói toàn bộ câu hỏi và câu trả lời vào file JSON.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            # ensure_ascii=False để giữ nguyên tiếng Việt không bị mã hóa unicode
            json.dump(answers, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Đã tạo file submission tại: {path}")
