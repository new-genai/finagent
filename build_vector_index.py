import os
import re
import gc
import pickle
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from src.metadata.normalizer import FinancialDataCleaner

ROOT_DIR = Path(__file__).resolve().parent
RAW_DIR = ROOT_DIR / "data" / "raw"
INDEX_DIR = ROOT_DIR / "data" / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def is_garbage_table(df, header_text):
    full_text = " ".join(df.astype(str).values.flatten()).lower()
    garbage_keywords = [
        "mục lục", "thông tin chung", "hội đồng quản trị", "ban giám đốc",
        "giấy chứng nhận", "đăng ký doanh nghiệp", "trang 1", "thành viên"
    ]
    if any(k in full_text for k in garbage_keywords):
        return True
    numeric_count = sum(
        1 for r in range(len(df)) for c in range(1, len(df.columns))
        if abs(FinancialDataCleaner.parse_vn_financial_number(df.iloc[r, c])) > 0.0
    )
    return numeric_count < 3

def build_index():
    logger.info("=" * 80)
    logger.info(f"🚀 KÍCH HOẠT THUẦN GPU RTX 3050 (TỐI ƯU BỘ NHỚ ZERO-COPY)...")
    logger.info("=" * 80)

    torch.cuda.empty_cache()
    gc.collect()

    logger.info("Đang nạp model lên VRAM GPU...")
    model = SentenceTransformer(
        MODEL_NAME, 
        device="cuda", 
        model_kwargs={"torch_dtype": torch.float16}
    )
    model.max_seq_length = 128

    txt_files = list(RAW_DIR.rglob("*.txt"))
    logger.info(f"Tìm thấy {len(txt_files)} file BCTC...")

    doc_store = []
    texts_to_embed = []

    for f_idx, f in enumerate(txt_files, 1):
        doc_id = re.sub(r'_extracted$', '', f.stem)
        m_ticker = re.search(r'^([A-Z0-9]+)_', f.name)
        m_year = re.search(r'(\d{4})', f.name)
        ticker = m_ticker.group(1).upper() if m_ticker else "UNKNOWN"
        year = m_year.group(1) if m_year else "YYYY"
        is_sep = "separate" in f.name.lower() or "rieng" in f.name.lower()
        rep_type = "separate" if is_sep else "consolidated"

        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as file:
                lines = file.readlines()

            for line_idx, line in enumerate(lines):
                if "<table" not in line.lower():
                    continue
                t_match = re.search(r'<table.*?>.*?</table>', line, re.DOTALL | re.IGNORECASE)
                if not t_match:
                    continue

                soup = BeautifulSoup(t_match.group(0), 'html.parser')
                t_elem = soup.find('table')
                if not t_elem:
                    continue

                rows = []
                for tr in t_elem.find_all('tr'):
                    cells = [re.sub(r'\s+', ' ', c.get_text()).strip() for c in tr.find_all(['td', 'th'])]
                    if cells and any(cells):
                        rows.append(cells)

                if len(rows) > 2:
                    import pandas as pd
                    max_cols = max(len(r) for r in rows)
                    df = pd.DataFrame([r + [''] * (max_cols - len(r)) for r in rows])
                    header_text = " ".join(df.iloc[0, :].astype(str)).lower()

                    if is_garbage_table(df, header_text):
                        continue

                    indicators = []
                    for r in range(1, min(12, len(df))):
                        lbl = str(df.iloc[r, 0]).strip()
                        if len(lbl) > 2 and not lbl.isdigit():
                            indicators.append(lbl)

                    summary_text = (
                        f"{ticker} {year} {rep_type} {header_text} "
                        f"{' '.join(indicators[:8])}"
                    )[:140]

                    table_info = {
                        "table_id": f"{doc_id}_table_{line_idx + 1}",
                        "doc_id": doc_id,
                        "company": ticker,
                        "year": year,
                        "report_type": rep_type,
                        "line_1based": line_idx + 1,
                        "headers": df.iloc[0, :].tolist(),
                        "summary": summary_text
                    }

                    doc_store.append(table_info)
                    texts_to_embed.append(summary_text)

        except Exception:
            continue

        if f_idx % 500 == 0 or f_idx == len(txt_files):
            logger.info(f"Đã quét {f_idx}/{len(txt_files)} file | Thu thập {len(doc_store)} bảng...")

    logger.info(f"\n⚡ ĐANG TÍNH TOÁN EMBEDDINGS BẰNG GPU RTX 3050 ({len(texts_to_embed)} bảng)...")
    
    # Encode trực tiếp ra float32 numpy mà không duplicate memory
    embeddings = model.encode(
        texts_to_embed,
        batch_size=256,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    logger.info("Đang ghi dữ liệu vào FAISS Index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32, copy=False))

    index_path = INDEX_DIR / "faiss.index"
    doc_store_path = INDEX_DIR / "doc_store.pkl"

    faiss.write_index(index, str(index_path))
    with open(doc_store_path, "wb") as f:
        pickle.dump({"doc_store": doc_store}, f)

    logger.info("=" * 80)
    logger.info(f"🎉 HOÀN TẤT! ĐÃ DỰNG THÀNH CÔNG VECTOR INDEX TRÊN GPU: {index.ntotal} VECTORS!")
    logger.info(f"📁 Lưu tại: {index_path} và {doc_store_path}")
    logger.info("=" * 80)

if __name__ == "__main__":
    build_index()