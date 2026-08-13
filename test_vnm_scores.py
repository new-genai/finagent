import sys
sys.path.append('.')
from pathlib import Path
from src.core.config import settings
from src.retrieval.bm25_retriever import BM25Retriever
from src.embedding.service import EmbeddingService
from src.retrieval.vector_index import FAISSIndex

bm25_idx = BM25Retriever()
index_dir = settings.INDEX_DIR
bm25_idx.load(index_dir / 'bm25.pkl')

embedder = EmbeddingService()
faiss_idx = FAISSIndex(dimension=embedder.dimension)
faiss_idx.load(index_dir / 'faiss')

question = 'doanh thu'
res = bm25_idx.search(question, top_k=3000)

print('--- VNM 2023 TABLES BM25 SCORES ---')
count = 0
for doc, score in res:
    if doc.get('company') == 'VNM' and str(doc.get('year')) == '2023':
        print(f"{score:.2f}: {doc.get('duckdb_table')}")
        count += 1
        if count >= 10: break

print('--- VNM 2023 TABLES FAISS SCORES ---')
query_emb = embedder.embed_text(question)
res2 = faiss_idx.search(query_emb, top_k=3000)
count = 0
for doc, score in res2:
    if doc.get('company') == 'VNM' and str(doc.get('year')) == '2023':
        print(f"{score:.2f}: {doc.get('duckdb_table')}")
        count += 1
        if count >= 10: break
