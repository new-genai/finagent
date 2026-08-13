import sys
sys.path.append('.')
from pathlib import Path
from src.core.config import settings
from src.retrieval.vector_index import FAISSIndex
from src.retrieval.bm25_retriever import BM25Retriever
from src.embedding.service import EmbeddingService

embedder = EmbeddingService()
faiss_idx = FAISSIndex(dimension=embedder.dimension)
bm25_idx = BM25Retriever()
index_dir = settings.INDEX_DIR
faiss_idx.load(index_dir / 'faiss')
bm25_idx.load(index_dir / 'bm25.pkl')

question = 'doanh thu vnm năm 2023'

print('--- BM25 TOP 10 ---')
res = bm25_idx.search(question, top_k=10)
for doc, score in res:
    print(f"{score:.2f}: {doc.get('duckdb_table')}")
    
print('--- FAISS TOP 10 ---')
query_emb = embedder.embed_text(question)
res2 = faiss_idx.search(query_emb, top_k=10)
for doc, score in res2:
    print(f"{score:.2f}: {doc.get('duckdb_table')}")
