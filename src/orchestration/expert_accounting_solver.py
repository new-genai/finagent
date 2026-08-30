import re
from difflib import SequenceMatcher
import pandas as pd
from src.metadata.normalizer import FinancialDataCleaner

class ExpertAccountingSolver:
    
    @staticmethod
    def detect_table_unit(context_text: str, df: pd.DataFrame) -> float:
        """Nhận diện đơn vị tiền tệ của bảng dựa trên văn bản và độ lớn số liệu."""
        ctx = context_text.lower()
        if "đơn vị tính: tỷ" in ctx or "đvt: tỷ" in ctx: return 1e9
        if "đơn vị tính: triệu" in ctx or "đvt: triệu" in ctx: return 1e6
        if "đơn vị tính: nghìn" in ctx or "đvt: nghìn" in ctx or "đvt: ngàn" in ctx: return 1e3
        if "đơn vị tính: usd" in ctx: return 1.0
        
        # Heuristic kiểm tra độ lớn của các ô số trong bảng
        max_val = 0.0
        for c in range(1, len(df.columns)):
            for r in range(min(5, len(df))):
                v = abs(FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c]))
                if v > max_val: max_val = v
                
        if max_val > 1e8: return 1.0     # Dữ liệu gốc là Đồng (VND)
        if max_val > 1e5: return 1e3     # Dữ liệu gốc là Nghìn VND
        return 1.0

    @staticmethod
    def detect_question_target_unit(q_text: str) -> float:
        q = q_text.lower()
        if any(k in q for k in ["phần trăm", "%", "tỷ lệ", "tỉ lệ", "tỷ trọng", "tỉ trọng", "lần", "ngày", "cổ phiếu", "cổ phần", "vòng"]):
            return -1.0  # Không scale tiền tệ
            
        if 'nghìn tỷ' in q or 'ngàn tỷ' in q: return 1e12
        if 'trăm tỷ' in q: return 1e11
        if 'tỷ đồng' in q or 'tỉ đồng' in q or 'tỷ' in q or 'tỉ' in q: return 1e9
        if 'triệu đồng' in q or 'triệu' in q: return 1e6
        if 'nghìn đồng' in q or 'ngàn đồng' in q: return 1e3
        return 1.0

    @classmethod
    def solve_single_metric(cls, q_text: str, target_year: str, lines: list, search_keywords: list) -> dict:
        q_lower = q_text.lower()
        q_target_unit = cls.detect_question_target_unit(q_text)
        is_ratio_query = (q_target_unit == -1.0)
        search_phrase = " ".join(search_keywords)
        
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
            
            rows = []
            for tr in re.findall(r'<tr.*?>(.*?)</tr>', t_match.group(0), re.DOTALL | re.IGNORECASE):
                cells = [re.sub(r'<.*?>', '', c).strip() for c in re.findall(r'<t[dh].*?>(.*?)</t[dh]>', tr, re.DOTALL | re.IGNORECASE)]
                if cells: rows.append(cells)
            if not rows or len(rows[0]) < 2: continue
            
            df = pd.DataFrame(rows)
            num_cols = len(df.columns)
            context_window = "".join(lines[max(0, line_idx - 6):line_idx])
            
            # Tính toán hệ số Scale tiền tệ
            if is_ratio_query:
                scale_factor = 1.0
            else:
                base_unit = cls.detect_table_unit(context_window, df)
                scale_factor = base_unit / q_target_unit
            
            table_bonus = 0.0
            ctx_lower = context_window.lower()
            if not is_ratio_query and any(k in ctx_lower for k in ["kết quả kinh doanh", "cân đối kế toán", "lưu chuyển tiền tệ"]):
                table_bonus = 50.0
            elif is_ratio_query and any(k in ctx_lower for k in ["công ty con", "công ty liên kết", "đầu tư", "sở hữu"]):
                table_bonus = 80.0
                
            for r in range(len(df)):
                row_label = str(df.iloc[r, 0]).strip().lower()
                if not row_label or row_label == "none": continue
                
                match_score = 0.0
                if search_phrase and search_phrase == row_label: match_score = 150.0
                elif search_phrase and search_phrase in row_label: match_score = 80.0
                else:
                    hits = sum(1 for kw in search_keywords if kw in row_label)
                    sim = SequenceMatcher(None, search_phrase, row_label).ratio()
                    if hits > 0: match_score = hits * 10.0 + sim * 20.0
                    
                total_score = match_score + table_bonus
                
                if match_score > 15.0 and total_score > max_score:
                    # Tìm cột phù hợp nhất trong dòng r
                    selected_col = -1
                    selected_val = 0.0
                    
                    if is_ratio_query:
                        # Đối với câu hỏi tỷ lệ: Quét tìm cột có giá trị trong khoảng (0, 100]
                        for c in range(num_cols - 1, 0, -1):
                            col_hdr = f"{df.columns[c]} {df.iloc[0, c]}".lower()
                            raw_v = abs(FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c]))
                            if any(k in col_hdr for k in ["biểu quyết", "sở hữu", "%", "tỷ lệ"]):
                                if 0 < raw_v <= 100.0:
                                    selected_col = c
                                    selected_val = raw_v
                                    break
                            elif 0 < raw_v <= 100.0 and selected_col == -1:
                                selected_col = c
                                selected_val = raw_v
                    else:
                        # Đối với câu hỏi tiền tệ: Tìm theo tiêu đề năm hoặc kỳ này
                        for c in range(1, num_cols):
                            col_hdr = f"{df.columns[c]} {df.iloc[0, c]}".lower()
                            if any(k in col_hdr for k in ["mã số", "thuyết minh", "tm"]): continue
                            raw_v = abs(FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c]))
                            if raw_v != 0.0:
                                if target_year in col_hdr or any(k in col_hdr for k in ["năm nay", "kỳ này", "31/12"]):
                                    selected_col = c
                                    selected_val = raw_v * scale_factor
                                    break
                                elif selected_col == -1:
                                    selected_col = c
                                    selected_val = raw_v * scale_factor
                                    
                    if selected_col != -1 and selected_val != 0.0:
                        max_score = total_score
                        best_val = selected_val
                        best_line = line_idx
                        best_df = df
                        best_r = r
                        best_c = selected_col
                        final_query = f"abs(float(df1.iloc[{r}, {selected_col}])) * {scale_factor if not is_ratio_query else 1.0}"

        return {
            "answer": best_val,
            "line": best_line,
            "df": best_df,
            "row": best_r,
            "col": best_c,
            "pandas_query": final_query,
            "score": max_score
        }