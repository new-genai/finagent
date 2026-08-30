import json
import re
from pathlib import Path
from difflib import SequenceMatcher
import pandas as pd
from src.metadata.normalizer import FinancialDataCleaner

COMPANY_MAP = {
    "vietjet": "VJC", "vjc": "VJC", "hàng không vietjet": "VJC",
    "á châu": "ACB", "ngân hàng á châu": "ACB", "acb": "ACB",
    "chứng khoán fpt": "FTS", "fpt securities": "FTS", "fts": "FTS",
    "fpt": "FPT", "tập đoàn fpt": "FPT",
    "đầu tư và phát triển việt nam": "BID", "bidv": "BID", "bid": "BID",
    "sabeco": "SAB", "bia - rượu - nước giải khát sài gòn": "SAB", "sab": "SAB",
    "saigonres": "SGR", "scr": "SCR", "địa ốc sài gòn thương tín": "SCR",
    "vincom retail": "VRE", "vre": "VRE", "vingroup": "VIC", "vic": "VIC",
    "hòa phát": "HPG", "hpg": "HPG", "hoa sen": "HSG", "hsg": "HSG",
    "thép nam kim": "NKG", "nkg": "NKG", "hà đô": "HDG", "hdg": "HDG",
    "đất xanh": "DXG", "dxg": "DXG", "bluemarq": "DXG",
    "hoàng huy": "HHS", "hhs": "HHS", "đèo cả": "HHV", "hhv": "HHV",
    "đức long gia lai": "DLG", "dlg": "DLG", "hoàng anh gia lai": "HAG", "hag": "HAG",
    "nông nghiệp quốc tế hoàng anh gia lai": "HNG", "hng": "HNG",
    "bảo việt": "BVH", "bvh": "BVH", "sao mai": "ASM", "asm": "ASM",
    "dệt may việt nam": "VGT", "vgt": "VGT",
    "quân đội": "MBB", "mbbank": "MBB", "mbb": "MBB",
    "ngoại thương việt nam": "VCB", "vietcombank": "VCB", "vcb": "VCB",
    "công thương việt nam": "CTG", "vietinbank": "CTG", "ctg": "CTG",
    "quốc tế việt nam": "VIB", "vib": "VIB", "shb": "SHB", "sài gòn - hà nội": "SHB",
    "sài gòn tài lộc": "STB", "sacombank": "STB", "stb": "STB",
    "hàng hải việt nam": "MSB", "msb": "MSB", "an bình": "ABB", "abb": "ABB",
    "bắc á": "BAB", "bab": "BAB", "nam á": "NAB", "nab": "NAB",
    "sài gòn công thương": "SGB", "sgb": "SGB", "kiên long": "KLB", "klb": "KLB",
    "quốc dân": "NVB", "ncb": "NVB", "nvb": "NVB",
    "petrolimex": "PLX", "plx": "PLX",
    "đạm cà mau": "DCM", "dcm": "DCM", "phân bón dầu khí cà mau": "DCM",
    "đạm phú mỹ": "DPM", "dpm": "DPM", "phân bón và hóa chất dầu khí": "DPM",
    "đại dương": "OGC", "ogc": "OGC", "hòa bình": "HBC", "hbc": "HBC",
    "gelex": "GEX", "gex": "GEX", "điện lực gelex": "GEE", "gee": "GEE",
    "điện lực dầu khí": "POW", "pow": "POW", "vận tải dầu khí": "PVT", "pvt": "PVT",
    "phát triển hạ tầng kỹ thuật": "IJC", "ijc": "IJC",
    "nam long": "NLG", "nlg": "NLG", "phát đạt": "PDR", "pdr": "PDR",
    "novaland": "NVL", "nvl": "NVL", "kinh bắc": "KBC", "kbc": "KBC",
    "viglacera": "VGC", "vgc": "VGC", "vinamilk": "VNM", "vnm": "VNM",
    "masan": "MSN", "msn": "MSN", "mch": "MCH", "thế giới di động": "MWG", "mwg": "MWG",
    "phú nhuận": "PNJ", "pnj": "PNJ", "dabaco": "DBC", "dbc": "DBC",
    "minh phú": "MPC", "mpc": "MPC", "đường quảng ngãi": "QNS", "qns": "QNS",
    "pc1": "PC1", "cre": "CRE", "vpi": "VPI", "ssh": "SSH", "hut": "HUT",
    "ht1": "HT1", "sam": "SAM", "gvr": "GVR", "acv": "ACV", "ceo": "CEO",
    "khg": "KHG", "vif": "VIF", "dnh": "DNH", "hnd": "HND", "snz": "SNZ", "dtk": "DTK", "bsr": "BSR"
}

STOP_WORDS = {
    "ctcp", "tmcp", "tnhh", "hđqt", "tctd", "tập", "đoàn", "công", "ty", "ngân", "hàng", "tổng",
    "mẹ", "riêng", "hợp", "nhất", "năm", "cuối", "đầu", "tại", "ngày", "là", "bao", "nhiêu",
    "triệu", "tỷ", "tỉ", "nghìn", "ngàn", "đồng", "phần", "trăm", "đến", "trong", "của", "và",
    "các", "thuộc", "vào", "khoản", "mục", "số", "hàng", "không", "mã"
}

def parse_html_table(table_html):
    rows = []
    for tr in re.findall(r'<tr.*?>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE):
        cells = [re.sub(r'<.*?>', '', c).strip() for c in re.findall(r'<t[dh].*?>(.*?)</t[dh]>', tr, re.DOTALL | re.IGNORECASE)]
        if cells: rows.append(cells)
    return pd.DataFrame(rows)

def get_multiplier(q_text):
    q = q_text.lower()
    if 'nghìn tỷ' in q or 'ngàn tỷ' in q: return 1e-12
    elif 'tỷ đồng' in q or 'tỉ đồng' in q or 'tỷ' in q or 'tỉ' in q: return 1e-9
    elif 'triệu đồng' in q or 'triệu' in q: return 1e-6
    elif 'trăm tỷ' in q: return 1e-11
    elif 'nghìn đồng' in q or 'ngàn đồng' in q: return 1e-3
    return 1.0

def extract_ticker(q_text, available_tickers):
    paren_match = re.search(r'\(([A-Za-z]{3,4})\)', q_text)
    if paren_match and paren_match.group(1).upper() in available_tickers:
        return paren_match.group(1).upper()
    q_lower = q_text.lower()
    for name_key in sorted(COMPANY_MAP.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(name_key) + r'\b', q_lower):
            sym = COMPANY_MAP[name_key]
            if sym in available_tickers: return sym
    for w in re.findall(r'\b[A-Za-z]{3,4}\b', q_text):
        if w.upper() in available_tickers and w.upper() not in {"CTCP", "TMCP", "TNHH", "HDQT", "TCTD", "VND", "USD"}:
            return w.upper()
    return "UNKNOWN"