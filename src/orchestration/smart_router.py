import re
from typing import Dict, Any, List

# BẢNG ÁNH XẠ ĐẦY ĐỦ TẤT CẢ DOANH NGHIỆP TRONG TẬP ĐỀ THI
FULL_COMPANY_MAP = {
    # Ngân hàng
    "sài gòn tài lộc": "STB",
    "sài gòn thương tín": "STB",
    "sacombank": "STB",
    "quân đội": "MBB",
    "mbbank": "MBB",
    "mb bank": "MBB",
    "sài gòn - hà nội": "SHB",
    "sài gòn hà nội": "SHB",
    "ngoại thương việt nam": "VCB",
    "vietcombank": "VCB",
    "công thương việt nam": "CTG",
    "vietinbank": "CTG",
    "đầu tư và phát triển việt nam": "BID",
    "bidv": "BID",
    "á châu": "ACB",
    "acb": "ACB",
    "hàng hải việt nam": "MSB",
    "hàng hải": "MSB",
    "msb": "MSB",
    "quốc tế việt nam": "VIB",
    "vib": "VIB",
    "quốc dân": "NVB",
    "ncb": "NVB",
    "nam á": "NAB",
    "nam a": "NAB",
    "namabank": "NAB",
    "an bình": "ABB",
    "abbank": "ABB",
    "bắc á": "BAB",
    "bac a": "BAB",
    "bacabank": "BAB",
    "phương đông": "OCB",
    "ocb": "OCB",
    "phát triển thành phố hồ chí minh": "HDB",
    "hdbank": "HDB",
    "xuất nhập khẩu việt nam": "EIB",
    "eximbank": "EIB",
    "kiên long": "KLB",
    "kienlongbank": "KLB",
    "sài gòn công thương": "SGB",
    "saigonbank": "SGB",
    "việt nam thịnh vượng": "VPB",
    "vpbank": "VPB",
    "việt á": "VAB",
    "vietabank": "VAB",
    "đông nam á": "SSB",
    "seabank": "SSB",

    # Bất động sản, Xây dựng, Hạ tầng
    "sunshine homes": "SSH",
    "giao thông đèo cả": "HHV",
    "đèo cả": "HHV",
    "đầu tư địa ốc no va": "NVL",
    "địa ốc no va": "NVL",
    "novaland": "NVL",
    "nova": "NVL",
    "xây dựng hòa bình": "HBC",
    "hòa bình": "HBC",
    "đức long gia lai": "DLG",
    "đức long": "DLG",
    "đất xanh": "DXG",
    "bất động sản đất xanh": "DXG",
    "dịch vụ bất động sản đất xanh": "DXS",
    "khải hoàn land": "KHG",
    "khải hoàn": "KHG",
    "nam long": "NLG",
    "hà đô": "HDG",
    "hado": "HDG",
    "đô thị kinh bắc": "KBC",
    "kinh bắc": "KBC",
    "c.e.o": "CEO",
    "ceo group": "CEO",
    "phát triển hạ tầng kỹ thuật": "IJC",
    "becamex ijc": "IJC",
    "đầu tư hạ tầng kỹ thuật": "CII",
    "đầu tư dịch vụ hoàng huy": "HHS",
    "hoàng huy": "HHS",
    "phát triển bất động sản phát đạt": "PDR",
    "phát đạt": "PDR",
    "văn phú invest": "VPI",
    "bất động sản văn phú": "VPI",
    "văn phú": "VPI",
    "hải phát": "HPX",
    "vincom retail": "VRE",
    "vingroup": "VIC",
    "bất động sản thế kỷ": "CRE",
    "cenland": "CRE",
    "tasco": "HUT",
    "sông đà": "SJG",
    "đầu tư phát triển xây dựng": "DIG",
    "dic corp": "DIG",
    "địa ốc sài gòn thương tín": "SCR",
    "ttc land": "SCR",

    # Sản xuất, Nông nghiệp, Tiêu dùng
    "bảo việt": "BVH",
    "công nghiệp cao su việt nam": "GVR",
    "cao su việt nam": "GVR",
    "cảng hàng không việt nam": "ACV",
    "thép nam kim": "NKG",
    "nam kim": "NKG",
    "masan": "MSN",
    "hàng tiêu dùng masan": "MCH",
    "masan meatlife": "MML",
    "masan high-tech materials": "MSR",
    "dabaco việt nam": "DBC",
    "dabaco": "DBC",
    "dệt may việt nam": "VGT",
    "vinatex": "VGT",
    "điện lực tkv": "DTK",
    "sữa việt nam": "VNM",
    "vinamilk": "VNM",
    "khí việt nam": "GAS",
    "pv gas": "GAS",
    "đường quảng ngãi": "QNS",
    "viglacera": "VGC",
    "hàng không vietjet": "VJC",
    "vietjet": "VJC",
    "tập đoàn gelex": "GEX",
    "gelex": "GEX",
    "điện lực gelex": "GEE",
    "thủy điện đa nhim - hàm thuận - đa mi": "DNH",
    "đa nhim": "DNH",
    "hòa phát": "HPG",
    "hoa sen": "HSG",
    "nông nghiệp quốc tế hoàng anh gia lai": "HNG",
    "hoàng anh gia lai": "HAG",
    "thủy sản minh phú": "MPC",
    "minh phú": "MPC",
    "container việt nam": "VSC",
    "viconship": "VSC",
    "điện gia lai": "GEG",
    "lâm nghiệp việt nam": "VIF",
    "vinafor": "VIF",
    "phân bón và hóa chất dầu khí": "DPM",
    "đạm phú mỹ": "DPM",
    "phân bón dầu khí cà mau": "DCM",
    "đạm cà mau": "DCM",
    "vận tải dầu khí": "PVT",
    "pvtrans": "PVT",
    "bia - rượu - nước giải khát sài gòn": "SAB",
    "sabeco": "SAB",
    "kỹ nghệ gỗ trường thành": "TTF",
    "gỗ trường thành": "TTF",
    "nhựa an phát xanh": "AAA",
    "an phát xanh": "AAA",
    "phát triển khu công nghiệp": "SNZ",
    "sonadezi": "SNZ",
    "xi măng vicem hà tiên": "HT1",
    "hà tiên": "HT1",
    "xăng dầu việt nam": "PLX",
    "petrolimex": "PLX",
    "lọc hóa dầu bình sơn": "BSR",
    "vàng bạc đá quý phú nhuận": "PNJ",
    "pnj": "PNJ",
    "thế giới di động": "MWG",
    "điện lực dầu khí việt nam": "POW",
    "pv power": "POW",
    "tập đoàn f.i.t": "FIT",
    "chứng khoán ssi": "SSI",
    "chứng khoán fpt": "FTS",
    "chứng khoán mb": "MBS",
    "fpt": "FPT",
    "bluemarq group": "BCG",
    "bamboo capital": "BCG",
    "sao mai": "ASM",
    "lương thực miền nam": "VSF",
    "vinafood 2": "VSF",
    "nhiệt điện hải phòng": "HND",
    "đại dương": "OGC",
    "ocean group": "OGC"
}

STOP_WORDS = {
    "của", "và", "là", "bao", "nhiêu", "trong", "năm", "ngày", "tháng", "tại", "đến", 
    "cho", "với", "các", "những", "được", "có", "vào", "thuộc", "theo", "trên", "tổng", 
    "công", "ty", "cổ", "phần", "tập", "đoàn", "ngân", "hàng", "tmcp", "ctcp", "đầu", "tư",
    "triệu", "đồng", "tỷ", "nghìn", "phần", "trăm", "tỉ", "kỳ", "trước", "sau", "cuối", "đầu"
}

class FinancialQueryRouter:

    @staticmethod
    def extract_years(text: str) -> List[int]:
        matches = re.findall(r'\b(201\d|202\d)\b', text)
        return sorted(list(set(int(m) for m in matches)))

    @staticmethod
    def extract_real_tickers(text: str) -> List[str]:
        t_lower = text.lower()
        matched_tickers = []
        
        # 1. Quét theo tên đầy đủ/thương mại từ dài đến ngắn
        sorted_keys = sorted(FULL_COMPANY_MAP.keys(), key=len, reverse=True)
        for name in sorted_keys:
            if name in t_lower:
                tk = FULL_COMPANY_MAP[name]
                if tk not in matched_tickers:
                    matched_tickers.append(tk)
                    
        # 2. Quét theo mã Ticker viết hoa 3-4 ký tự
        words = re.findall(r'\b[A-Z0-9]{3,4}\b', text)
        for w in words:
            if w in FULL_COMPANY_MAP.values() and w not in matched_tickers:
                matched_tickers.append(w)
                
        return matched_tickers

    @classmethod
    def route(cls, q_id: int, question: str) -> Dict[str, Any]:
        years = cls.extract_years(question)
        tickers = cls.extract_real_tickers(question)
        return {
            "tickers": tickers,
            "years": years
        }