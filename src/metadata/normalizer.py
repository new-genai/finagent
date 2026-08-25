import re
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class TermNormalizer:
    """Normalizes financial terms using a predefined dictionary."""
    def __init__(self):
        self.term_mapping = {
            "doanh thu thu n": "net_revenue",
            "revenue": "net_revenue",
            "net revenue": "net_revenue",
            "sales": "net_revenue",
            "doanh thu": "net_revenue",
            "l i nhu n": "profit",
            "profit": "profit",
            "net profit": "profit",
            "l i nhu n sau thu ": "profit",
            "t n": "assets",
            "t ng t n": "assets",
            "assets": "assets",
            "ti t": "cash",
            "cash": "cash",
            "h ng t n kho": "inventory",
            "inventory": "inventory",
            "h ng kho": "inventory"
        }
             
    def normalize(self, term: str) -> str:
        if not term:
            return ""
        normalized = term.strip().lower()
        if normalized in self.term_mapping:
            return self.term_mapping[normalized]
        for key, value in self.term_mapping.items():
            if key in normalized:
                return value
        return normalized

class FinancialDataCleaner:
    """Chuẩn hóa chuỗi số tài chính Việt Nam sang kiểu Float an toàn."""
    @staticmethod
    def parse_vn_financial_number(val) -> float:
        if pd.isna(val) or val is None:
            return np.nan
        if isinstance(val, (int, float)):
            return float(val)
            
        s = str(val).strip().replace('\u200b', '').replace('\xa0', '')
        if not s or s in ['-', ' ', '—', '_', 'N/A', 'n/a', 'na', 'null', 'None']:
            return 0.0
            
        # Kiểm tra xem có chứa chữ cái tiếng Việt hoặc tiếng Anh không (bỏ qua 'vnd', 'usd')
        test_str = s.lower().replace("vnd", "").replace("usd", "").strip()
        if re.search(r'[a-zđáàãạảăâấầẫẩậắằẵặẳéèẽẹẻêếềễệểíìĩịỉóòõọỏôốồỗộổơớờỡợởúùũụủưứừữựửýỳỹỵỷ]', test_str):
            return np.nan # Trả về NaN để TableExtractor nhận biết đây là Text và giữ nguyên
            
        is_negative = False
        if (s.startswith('(') and s.endswith(')')) or (s.startswith('[') and s.endswith(']')):
            is_negative = True
            s = s[1:-1].strip()
        elif s.startswith('-'):
            is_negative = True
            s = s[1:].strip()
            
        # Xử lý định dạng dấu chấm/phẩy kiểu Việt Nam
        if '.' in s and ',' in s:
            if s.rfind(',') > s.rfind('.'):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif ',' in s:
            parts = s.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                s = s.replace(',', '.')
            else:
                s = s.replace(',', '')
        elif '.' in s:
            parts = s.split('.')
            if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
                s = s.replace('.', '')
                
        clean_str = re.sub(r'[^\d.]', '', s)
        try:
            num = float(clean_str)
            return -num if is_negative else num
        except ValueError:
            return np.nan