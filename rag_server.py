import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from src.core.config import settings
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.schemas.core import RetrievedTable

app = FastAPI(title="FinAgent RAG Engine")

# Nạp dữ liệu và GPU Model một lần duy nhất vào bộ nhớ
index_dir = settings.INDEX_DIR
bm25_idx = BM25Retriever(index_path=str(index_dir / "bm25.pkl"))
dense_idx = DenseRetriever(
    index_path=str(index_dir / "faiss.index"),
    doc_store_path=str(index_dir / "bm25.pkl")
)
retriever = HybridRetriever(bm25_retriever=bm25_idx, dense_retriever=dense_idx)

class QueryPayload(BaseModel):
    sub_query: str
    company: Optional[str] = None
    year: Optional[str] = None
    top_k: int = 3

@app.post("/retrieve", response_model=List[RetrievedTable])
def search_tables(payload: QueryPayload):
    return retriever.retrieve_single(
        sub_query=payload.sub_query,
        company=payload.company,
        year=payload.year,
        top_k=payload.top_k
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)