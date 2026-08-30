import re
from typing import Dict, Any, List, Optional
import pandas as pd
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from src.metadata.normalizer import FinancialDataCleaner

class DeterministicTableEngine:
    """
    Engine trích xuất số liệu tài chính không dùng LLM,
    sử dụng thuật toán so khớp Token-Set Ratio và cân bằng đơn vị tự động.
    """

    @staticmethod
    def html_to_clean_matrix(table_html: str) -> Optional[pd.DataFrame]:
        try:
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')
            if not table: return None
            
            rows = []
            for tr in table.find_all('tr'):
                cells = [re.sub(r'\s+', ' ', cell.get_text()).strip() for cell in tr.find_all(['td', 'th'])]
                if cells and any(cells): rows.append(cells)
                    
            if not rows or len(rows[0]) < 2: return None
            max_cols = max(len(r) for r in rows)
            padded_rows = [r + [''] * (max_cols - len(r)) for r in rows]
            return pd.DataFrame(padded_rows)
        except Exception:
            return None

    @staticmethod
    def auto_scale(q_text: str, raw_val: float) -> float:
        """Tự động chuẩn hóa đơn vị tính dựa trên câu hỏi và độ lớn số liệu."""
        q_lower = q_text.lower()
        if any(k in q_lower for k in ["phần trăm", "%", "tỷ lệ", "tỉ lệ", "tỷ trọng", "tỉ trọng", "lần", "ngày", "cổ phiếu", "vòng"]):
            return 1.0  # Không đổi đơn vị với chỉ số tỷ lệ

        abs_v = abs(raw_val)
        
        # Câu hỏi yêu cầu đơn vị Triệu đồng
        if 'triệu đồng' in q_lower or 'triệu' in q_lower:
            if abs_v >= 1e8: return 1e-6   # Bảng ghi VND
            if abs_v >= 1e5: return 1e-3   # Bảng ghi Nghìn VND
            return 1.0
            
        # Câu hỏi yêu cầu đơn vị Tỷ đồng
        if any(k in q_lower for k in ['tỷ đồng', 'tỉ đồng', 'tỷ', 'tỉ']):
            if abs_v >= 1e8: return 1e-9   # Bảng ghi VND
            if abs_v >= 1e5: return 1e-6   # Bảng ghi Nghìn VND
            if abs_v >= 1e2: return 1e-3   # Bảng ghi Triệu VND
            return 1.0

        # Câu hỏi yêu cầu đơn vị Nghìn đồng
        if 'nghìn đồng' in q_lower or 'ngàn đồng' in q_lower:
            if abs_v >= 1e8: return 1e-3
            return 1.0
            
        return 1.0

    @classmethod
    def query_table(cls, q_text: str, target_year: str, lines: List[str], core_query: str) -> Dict[str, Any]:
        q_lower = q_text.lower()
        is_ratio_query = any(k in q_lower for k in ["phần trăm", "%", "tỷ lệ", "tỉ lệ", "tỷ trọng", "tỉ trọng", "lợi ích", "quyền biểu quyết", "biểu quyết"])
        
        best_val = 0.0
        best_line = 0
        best_df = None
        best_r = 0
        best_c = 1
        max_score = 0.0
        final_query = ""

        for line_idx, line in enumerate(lines):
            if "<table" not in line.lower(): continue
            t_match = re.search(r'<table.*?>.*?</table>', line, re.DOTALL | re.IGNORECASE)
            if not t_match: continue
                
            df = cls.html_to_clean_matrix(t_match.group(0))
            if df is None or df.shape[1] < 2: continue
            
            num_rows, num_cols = df.shape
            
            for r in range(num_rows):
                row_label = str(df.iloc[r, 0]).strip().lower()
                if not row_label or row_label == "none" or len(row_label) < 2: continue
                
                # Sử dụng RapidFuzz Token Set Ratio (khớp cụm từ không phân biệt thứ tự)
                score = fuzz.token_set_ratio(core_query.lower(), row_label)
                
                if score > max_score and score >= 60.0:
                    sel_col = -1
                    sel_val = 0.0
                    scale = 1.0
                    
                    if is_ratio_query:
                        # Tìm cột % (thường ở các cột cuối cùng)
                        for c in range(num_cols - 1, 0, -1):
                            col_txt = f"{df.columns[c]} {df.iloc[0, c]}".lower()
                            val_c = abs(FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c]))
                            if any(k in col_txt for k in ["tỷ lệ", "sở hữu", "biểu quyết", "quyền", "%"]) and 0 < val_c <= 100.0:
                                sel_col = c
                                sel_val = val_c
                                break
                            elif 0 < val_c <= 100.0 and sel_col == -1:
                                sel_col = c
                                sel_val = val_c
                    else:
                        # Tìm cột số tiền theo năm
                        for c in range(1, num_cols):
                            col_txt = f"{df.columns[c]} {df.iloc[0, c]}".lower()
                            if any(k in col_txt for k in ["mã số", "thuyết minh", "tm", "note"]): continue
                            val_c = abs(FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c]))
                            if val_c != 0.0:
                                scale = cls.auto_scale(q_text, val_c)
                                if target_year in col_txt or any(k in col_txt for k in ["năm nay", "kỳ này", "31/12"]):
                                    sel_col = c
                                    sel_val = val_c * scale
                                    break
                                elif sel_col == -1:
                                    sel_col = c
                                    sel_val = val_c * scale
                                    
                    if sel_col != -1 and sel_val != 0.0:
                        max_score = score
                        best_val = sel_val
                        best_line = line_idx
                        best_df = df
                        best_r = r
                        best_c = sel_col
                        final_query = f"abs(float(df1.iloc[{r}, {sel_col}])) * {scale if not is_ratio_query else 1.0}"

        return {
            "answer": best_val,
            "line": best_line,
            "df": best_df,
            "row": best_r,
            "col": best_c,
            "pandas_query": final_query,
            "score": max_score
        }