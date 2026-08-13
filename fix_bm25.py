import json
from pathlib import Path
import sys
sys.path.append('.')
from src.retrieval.bm25_retriever import BM25Retriever
from src.core.config import settings

schema_path = Path('data/metadata/schemas.json')
schemas = json.loads(schema_path.read_text(encoding='utf-8'))
allowed_tickers = {'VNM', 'HPG', 'FPT', 'MWG', 'VJC', 'ACB', 'FTS', 'SCR', 'VSC', 'HT1', 'SAM', 'SSH'}
allowed_years = {'2022', '2023'}

valid_schemas = []
for s in schemas:
    c = str(s.get('company', '')).upper()
    y = str(s.get('year', ''))
    if c in allowed_tickers and y in allowed_years:
        valid_schemas.append(s)

bm25 = BM25Retriever()
bm25.build(valid_schemas)
bm25.save(settings.INDEX_DIR / 'bm25.pkl')
print('BM25 BUILT AND SAVED PROPERLY!')
