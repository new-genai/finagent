import re
import pandas as pd
from typing import Optional, List

def parse_vietnamese_number(val: any) -> Optional[float]:
    if pd.isna(val): return None
    s = str(val).strip()
    
    # CHẶN ĐỨNG VIỆC DÍNH SỐ: Cắt bằng mọi loại khoảng trắng/xuống dòng và chỉ lấy số đầu
    s = re.split(r'[\s\n\xa0\u200b]+', s)[0]
    
    is_negative = False
    if (s.startswith('(') and s.endswith(')')) or s.startswith('-'):
        is_negative = True
        
    s = re.sub(r'[^\d\,\.]', '', s)
    if not s: return None
    
    if '.' in s and ',' in s:
        if s.rfind('.') > s.rfind(','): s = s.replace(',', '')
        else: s = s.replace('.', '').replace(',', '.')
    else:
        if '.' in s and len(s) - s.rfind('.') == 4: s = s.replace('.', '')
        elif ',' in s and len(s) - s.rfind(',') == 4: s = s.replace(',', '')
        else: s = s.replace(',', '.')
        
    try:
        res = float(s)
        if int(res) in [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]: return None
        if res.is_integer(): res = int(res)
        return -res if is_negative else res
    except:
        return None

def extract_financial_metric(dfs: dict, keywords: List[str], year: str, get_max: bool = True) -> Optional[float]:
    found_vals = []
    for df in dfs.values():
        try:
            s_name = df.iloc[:, 0] if not isinstance(df.iloc[:, 0], pd.DataFrame) else df.iloc[:, 0].iloc[:, 0]
            s_str = s_name.astype(str).str.lower().str.strip()
            
            mask = pd.Series(False, index=s_name.index)
            for kw in keywords:
                kw = str(kw).lower().strip()
                # 1. Khớp chính xác (nếu giống hoàn toàn chuỗi)
                mask = mask | s_str.str.contains(kw, case=False, na=False, regex=False)
                
                # 2. Khớp theo từng từ (Fuzzy match)
                kw_words = kw.split()
                if len(kw_words) > 1:
                    word_mask = pd.Series(True, index=s_name.index)
                    for w in kw_words:
                        word_mask = word_mask & s_str.str.contains(w, case=False, na=False, regex=False)
                    mask = mask | word_mask
                
            if not mask.any(): continue
            
            col = None
            for c in df.columns[1:]:
                c_str = str(c).lower()
                if 'thuyết minh' in c_str or 'mã' in c_str: continue
                if str(year) in c_str or 'nay' in c_str or 'cuối' in c_str:
                    col = c; break
                    
            if col is None:
                for c in df.columns[1:]:
                    c_str = str(c).lower()
                    if 'thuyết minh' not in c_str and 'mã' not in c_str:
                        col = c; break
                        
            if col is not None:
                c_data = df[col] if not isinstance(df[col], pd.DataFrame) else df[col].iloc[:, 0]
                vals = c_data[mask].apply(parse_vietnamese_number).dropna()
                if not vals.empty:
                    found_vals.extend(vals.tolist())
        except Exception:
            continue
            
    if not found_vals: return None
    return max(found_vals) if get_max else found_vals[0]
