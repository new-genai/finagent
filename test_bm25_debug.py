import sys
sys.path.append('.')
from pathlib import Path
from src.core.config import settings
from src.retrieval.bm25_retriever import BM25Retriever

bm25_idx = BM25Retriever()
index_dir = settings.INDEX_DIR
bm25_idx.load(index_dir / 'bm25.pkl')

print(f"Num docs in BM25: {len(bm25_idx.doc_store)}")
if hasattr(bm25_idx, 'bm25'):
    print(f"BM25 corpus size: {bm25_idx.bm25.corpus_size}")
else:
    print("NO BM25!")

question = 'doanh thu'
res = bm25_idx.search(question, top_k=3000)
print(f'Total results: {len(res)}')
for doc, score in res[:5]:
    print(f"{score:.2f}: {doc.get('duckdb_table')}")

print('VNM 2023 results:')
count = 0
for doc, score in res:
    if doc.get('company') == 'VNM' and str(doc.get('year')) == '2023':
        print(f"{score:.2f}: {doc.get('duckdb_table')}")
        count += 1
        if count > 5: break
