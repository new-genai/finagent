import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import logging
import pickle

from src.parser.report_parser import FinancialReportParser
from src.metadata.builders import SchemaBuilder
from src.exporter.csv_exporter import CSVExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = ROOT / "data" / "raw" / "ViFinQA"
PROCESSED_CSV = ROOT / "data" / "processed" / "csv"
INDEX_DIR = ROOT / "data" / "index"

PROCESSED_CSV.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

logger.info("1. PARSE VÀ XUẤT CSV TỪ DỮ LIỆU GỐC...")
parser = FinancialReportParser()
exporter = CSVExporter()
schema_builder = SchemaBuilder()

all_schemas = []
txt_files = list(RAW_DIR.rglob("*.txt"))

for idx, fpath in enumerate(txt_files, 1):
    try:
        report = parser.parse(fpath)
        exporter.export(report, PROCESSED_CSV)
        schemas = schema_builder.build_schema(report)
        all_schemas.extend(schemas)
        if idx % 20 == 0 or idx == len(txt_files):
            logger.info(f"Đã xử lý {idx}/{len(txt_files)} files...")
    except Exception as e:
        logger.error(f"Lỗi parse {fpath.name}: {e}")

logger.info(f"Tổng cộng có {len(all_schemas)} bảng dữ liệu.")

logger.info("2. TẠO INDEX BM25 / DOC_STORE...")
# Chỉ lưu metadata nhẹ để tránh MemoryError khi load
doc_store = [
    {
        "table_id": s.get("table_id"),
        "duckdb_table": s.get("duckdb_table"),
        "company": s.get("company"),
        "year": str(s.get("year")),
        "title": s.get("title"),
        "headers": s.get("headers", []),
        "keywords": s.get("keywords", [])[:15]
    }
    for s in all_schemas
]

with open(INDEX_DIR / "bm25.pkl", "wb") as f:
    pickle.dump({"doc_store": doc_store}, f, protocol=pickle.HIGHEST_PROTOCOL)

logger.info("✅ HOÀN TẤT BUILD INDEX NHẸ!")