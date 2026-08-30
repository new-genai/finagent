import re
from typing import Dict, Any, List, Optional
import pandas as pd
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from src.metadata.normalizer import FinancialDataCleaner

class AnchoredFinancialEngine:
    """
    Engine tài chính chuyên dụng định vị chính xác Báo cáo chính thức (IS, BS, CF)
    trước khi trích xuất, loại bỏ hoàn toàn bẫy bảng thuyết minh con.
    """

    @staticmethod
    def html_to_dataframe(table_html: str) -> Optional[pd.DataFrame]:
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

    @classmethod
    def identify_statement_type(cls, df: pd.DataFrame) -> str:
        """Nhận diện loại Báo cáo tài chính dựa trên các chỉ tiêu neo chuẩn."""
        full_text = " ".join(df.iloc[:, 0].astype(str)).lower()
        if "doanh thu thuần" in full_text and "lợi nhuận sau thuế" in full_text:
            return "IS"  # Báo cáo Kết quả Kinh doanh
        if "tổng cộng tài sản" in full_text or ("tài sản ngắn hạn" in full_text and "vốn chủ sở hữu" in full_text):
            return "BS"  # Bảng Cân đối Kế toán
        if "lưu chuyển tiền thuần từ hoạt động kinh doanh" in full_text:
            return "CF"  # Báo cáo Lưu chuyển Tiền tệ
        return "NOTES"  # Thuyết minh

    @classmethod
    def resolve_correct_column(cls, df: pd.DataFrame, target_year: str) -> int:
        """Định vị chính xác cột số liệu năm đích, loại bỏ cột mã số/thuyết minh."""
        num_cols = len(df.columns)
        for c in range(1, num_cols):
            hdr = f"{df.columns[c]} {df.iloc[0, c]} {df.iloc[1, c] if len(df) > 1 else ''}".lower()
            if any(k in hdr for k in ["mã số", "thuyết minh", "tm", "note"]): continue
            if target_year in hdr or any(k in hdr for k in ["năm nay", "kỳ này", "31/12"]):
                return c
        return 1

    @classmethod
    def calculate_scale(cls, q_text: str, raw_val: float) -> float:
        q_lower = q_text.lower()
        if any(k in q_lower for k in ["phần trăm", "%", "tỷ lệ", "tỉ lệ", "tỷ trọng", "tỉ trọng", "lần", "ngày", "cổ phiếu"]):
            return 1.0
        abs_v = abs(raw_val)
        if 'triệu đồng' in q_lower or 'triệu' in q_lower:
            if abs_v >= 1e8: return 1e-6
            if abs_v >= 1e5: return 1e-3
            return 1.0
        if any(k in q_lower for k in ['tỷ đồng', 'tỉ đồng', 'tỷ', 'tỉ']):
            if abs_v >= 1e8: return 1e-9
            if abs_v >= 1e5: return 1e-6
            if abs_v >= 1e2: return 1e-3
            return 1.0
        if 'nghìn đồng' in q_lower or 'ngàn đồng' in q_lower:
            if abs_v >= 1e8: return 1e-3
            return 1.0
        return 1.0

    @classmethod
    def execute_query(cls, q_text: str, target_year: str, lines: List[str], core_query: str) -> Dict[str, Any]:
        q_lower = q_text.lower()
        is_ratio = any(k in q_lower for k in ["phần trăm", "%", "tỷ lệ", "tỉ lệ", "tỷ trọng", "tỉ trọng", "lợi ích", "quyền biểu quyết", "biểu quyết"])
        
        # Xác định Báo cáo mục tiêu dựa trên câu hỏi
        preferred_stmt = "NOTES"
        if any(k in q_lower for k in ["doanh thu", "lợi nhuận", "giá vốn", "chi phí tài chính", "chi phí quản lý", "chi phí bán hàng", "lãi thuần"]):
            preferred_stmt = "IS"
        elif any(k in q_lower for k in ["tài sản", "nợ phải trả", "vốn chủ sở hữu", "tiền và tương đương", "hàng tồn kho", "phải thu", "phải trả"]):
            preferred_stmt = "BS"
        elif any(k in q_lower for k in ["lưu chuyển tiền", "tiền thu", "tiền chi"]):
            preferred_stmt = "CF"

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
                
            df = cls.html_to_dataframe(t_match.group(0))
            if df is None or df.shape[1] < 2: continue
            
            stmt_type = cls.identify_statement_type(df)
            stmt_bonus = 100.0 if stmt_type == preferred_stmt and preferred_stmt != "NOTES" else 0.0
            
            target_col = cls.resolve_correct_column(df, target_year)
            
            for r in range(len(df)):
                row_label = str(df.iloc[r, 0]).strip().lower()
                if not row_label or row_label == "none" or len(row_label) < 2: continue
                
                score = fuzz.token_set_ratio(core_query.lower(), row_label) + stmt_bonus
                
                if score > max_score and score >= 65.0:
                    raw_val = FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, target_col])
                    if raw_val != 0.0:
                        scale = cls.calculate_scale(q_text, raw_val)
                        val = abs(raw_val) * scale
                        
                        max_score = score
                        best_val = val
                        best_line = line_idx
                        best_df = df
                        best_r = r
                        best_c = target_col
                        final_query = f"abs(float(df1.iloc[{r}, {target_col}])) * {scale if not is_ratio else 1.0}"

        return {
            "answer": best_val,
            "line": best_line,
            "df": best_df,
            "row": best_r,
            "col": best_c,
            "pandas_query": final_query,
            "score": max_score
        }