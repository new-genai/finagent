import re
from typing import Dict, Any, List, Optional
import pandas as pd
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from src.metadata.normalizer import FinancialDataCleaner

class DuckDBFinancialEngine:

    @staticmethod
    def html_to_dataframe(table_html: str) -> Optional[pd.DataFrame]:
        try:
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')
            if not table: 
                return None
            rows = []
            for tr in table.find_all('tr'):
                cells = [re.sub(r'\s+', ' ', cell.get_text()).strip() for cell in tr.find_all(['td', 'th'])]
                if cells and any(cells): 
                    rows.append(cells)
            if not rows or len(rows[0]) < 2: 
                return None
            max_cols = max(len(r) for r in rows)
            return pd.DataFrame([r + [''] * (max_cols - len(r)) for r in rows])
        except Exception:
            return None

    @staticmethod
    def calculate_scale(q_text: str, raw_val: float) -> float:
        q_lower = q_text.lower()
        if any(k in q_lower for k in ["phần trăm", "%", "tỷ lệ", "tỉ lệ", "tỷ trọng", "tỉ trọng", "lần", "ngày", "cổ phiếu"]):
            return 1.0
            
        abs_v = abs(raw_val)
        if 'nghìn tỷ' in q_lower or 'ngàn tỷ' in q_lower:
            if abs_v >= 1e11: return 1e-12
            if abs_v >= 1e8: return 1e-9
            return 1.0
        if any(k in q_lower for k in ['tỷ đồng', 'tỉ đồng', 'tỷ', 'tỉ']):
            if abs_v >= 1e8: return 1e-9
            if abs_v >= 1e5: return 1e-6
            if abs_v >= 1e2: return 1e-3
            return 1.0
        if 'triệu đồng' in q_lower or 'triệu' in q_lower:
            if abs_v >= 1e8: return 1e-6
            if abs_v >= 1e5: return 1e-3
            return 1.0
        if 'nghìn đồng' in q_lower or 'ngàn đồng' in q_lower:
            if abs_v >= 1e8: return 1e-3
            return 1.0
        return 1.0

    @classmethod
    def execute_duckdb_lookup(cls, q_text: str, target_year: str, lines: List[str], keywords: List[str]) -> Dict[str, Any]:
        q_lower = q_text.lower()
        is_ratio = any(k in q_lower for k in ["phần trăm", "%", "tỷ lệ", "tỉ lệ", "tỷ trọng", "tỉ trọng", "quyền biểu quyết", "biểu quyết", "lợi ích"])
        is_exec = any(k in q_lower for k in ["thù lao", "ông ", "bà ", "chủ tịch", "thành viên hđqt", "ban giám đốc", "tổng giám đốc"])
        is_growth = any(k in q_lower for k in ["tăng trưởng", "tăng bao nhiêu", "giảm bao nhiêu", "chênh lệch", "thay đổi", "biến động", "so với năm"])
        
        search_str = " ".join(keywords).lower()
        
        best_val = 0.0
        best_line = 0
        best_df = None
        best_r = 0
        best_c = 1
        max_score = 0.0
        final_query = ""

        for line_idx, line in enumerate(lines):
            if "<table" not in line.lower(): 
                continue
            t_match = re.search(r'<table.*?>.*?</table>', line, re.DOTALL | re.IGNORECASE)
            if not t_match: 
                continue
                
            df = cls.html_to_dataframe(t_match.group(0))
            if df is None or df.shape[1] < 2: 
                continue
            
            full_first_col = " ".join(df.iloc[:, 0].astype(str)).lower()
            bonus = 0.0
            
            # Phân biệt ngữ cảnh bảng biểu chính xác
            if is_exec:
                if any(k in full_first_col for k in ["thù lao", "ông", "bà", "hđqt", "hội đồng quản trị", "thành viên"]):
                    bonus = 50.0
            else:
                if "doanh thu thuần" in full_first_col and "lợi nhuận sau thuế" in full_first_col:
                    bonus = 45.0  # Báo cáo KQKD chính
                elif "tổng cộng tài sản" in full_first_col or "tài sản ngắn hạn" in full_first_col:
                    bonus = 45.0  # Bảng CĐKT chính
                elif "lưu chuyển tiền thuần" in full_first_col:
                    bonus = 35.0  # Báo cáo LCTT chính

            for r in range(len(df)):
                row_label = str(df.iloc[r, 0]).strip().lower()
                if not row_label or row_label == "none" or len(row_label) < 2: 
                    continue
                
                # Tránh nhầm lẫn chỉ tiêu Lợi nhuận chưa phân phối ở CĐKT khi câu hỏi hỏi LNST kinh doanh
                if "lợi nhuận sau thuế" in search_str and "chưa phân phối" in row_label and "chưa phân phối" not in q_lower:
                    continue

                score = 0.0
                if search_str and search_str == row_label: 
                    score = 150.0 + bonus
                elif search_str and search_str in row_label: 
                    score = 85.0 + bonus
                elif keywords:
                    hits = sum(1 for kw in keywords if kw in row_label)
                    sim = SequenceMatcher(None, search_str, row_label).ratio()
                    if hits > 0: 
                        score = hits * 15.0 + sim * 35.0 + bonus

                if score > max_score and score >= 20.0:
                    sel_col = -1
                    sel_val = 0.0
                    scale = 1.0

                    if is_ratio:
                        for c in range(len(df.columns) - 1, 0, -1):
                            val_c = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c])
                            col_txt = f"{df.columns[c]} {df.iloc[0, c]}".lower()
                            if any(k in col_txt for k in ["tỷ lệ", "sở hữu", "biểu quyết", "quyền", "%"]) and 0 < abs(val_c) <= 100.0:
                                sel_col, sel_val = c, val_c
                                break
                            elif 0 < abs(val_c) <= 100.0 and sel_col == -1:
                                sel_col, sel_val = c, val_c
                        if sel_col != -1:
                            final_query = f"float(df1.iloc[{r}, {sel_col}])"
                    elif is_growth and len(df.columns) >= 3:
                        val_c1 = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, 1])
                        val_c2 = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, 2])
                        scale = cls.calculate_scale(q_text, val_c1)
                        sel_val = (val_c1 - val_c2) * scale
                        sel_col = 1
                        final_query = f"(float(df1.iloc[{r}, 1]) - float(df1.iloc[{r}, 2])) * {scale}"
                    else:
                        for c in range(1, len(df.columns)):
                            col_txt = f"{df.columns[c]} {df.iloc[0, c]}".lower()
                            if any(k in col_txt for k in ["mã số", "thuyết minh", "tm", "note"]): 
                                continue
                            val_c = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c])
                            if val_c != 0.0:
                                scale = cls.calculate_scale(q_text, val_c)
                                if target_year in col_txt or any(k in col_txt for k in ["năm nay", "kỳ này", "31/12"]):
                                    sel_col, sel_val = c, val_c * scale
                                    break
                                elif sel_col == -1:
                                    sel_col, sel_val = c, val_c * scale
                        if sel_col != -1:
                            final_query = f"float(df1.iloc[{r}, {sel_col}]) * {scale}"

                    if sel_col != -1 and sel_val != 0.0:
                        max_score = score
                        best_val = sel_val
                        best_line = line_idx
                        best_df = df
                        best_r = r
                        best_c = sel_col

        return {
            "answer": best_val,
            "line": best_line,
            "df": best_df,
            "row": best_r,
            "col": best_c,
            "pandas_query": final_query if final_query else "0.0",
            "score": max_score
        }